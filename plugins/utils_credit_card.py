import json
from json.decoder import JSONDecodeError

from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters
from tools.sessions import session

"""
data/command.yml

credit:
  cmd: crt
  format: crt <bin 4-8位数字>
  usage: 查询信用卡简略信息

"""


@Client.on_message(command("credit"))
async def card(_: Client, message: Message):
    await message.edit_text("正在查询中...")
    cmd, args = Parameters.get(message)
    try:
        card_bin = args
    except ValueError:
        await message.edit_text("出错了呜呜呜 ~ 无效的参数。")
        return
    try:
        r = await session.get(f"https://lookup.binlist.net/{card_bin}", timeout=5.5)
    except Exception:
        await message.edit_text("出错了呜呜呜 ~ 无法访问到binlist。")
        return
    if r.status_code == 404:
        await message.edit_text("出错了呜呜呜 ~ 目标卡头不存在")
        return
    if r.status_code == 429:
        await message.edit_text("出错了呜呜呜 ~ 每分钟限额超过，请等待一分钟再试")
        return

    try:
        bin_json = json.loads(r.content.decode("utf-8"))
    except JSONDecodeError:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return

    msg_out = [f"BIN：{card_bin}"]
    try:
        msg_out.extend(["卡品牌：" + bin_json["scheme"]])
    except (KeyError, TypeError):
        pass
    try:
        msg_out.extend(["卡类型：" + bin_json["type"]])
    except (KeyError, TypeError):
        pass
    try:
        msg_out.extend(["卡种类：" + bin_json["brand"]])
    except (KeyError, TypeError):
        pass
    try:
        msg_out.extend(["发卡行：" + bin_json["bank"]["name"]])
    except (KeyError, TypeError):
        pass
    try:
        if bin_json["prepaid"]:
            msg_out.extend(["是否预付：是"])
        else:
            msg_out.extend(["是否预付：否"])
    except (KeyError, TypeError):
        pass
    try:
        msg_out.extend(["发卡国家：" + bin_json["country"]["name"]])
    except (KeyError, TypeError):
        pass
    await message.edit_text("\n".join(msg_out))
