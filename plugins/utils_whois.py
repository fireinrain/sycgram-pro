from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters
from tools.sessions import session

"""
data/command.yml

whois:
  cmd: whois
  format: -whois <域名>
  usage: 查看域名是否已被注册、注册日期、过期日期、域名状态、DNS解析服务器等。
"""


@Client.on_message(command("whois"))
async def whois(_: Client, message: Message):
    cmd, args = Parameters.get(message)
    hostname = args
    if not hostname:
        await message.edit_text("无效参数,使用指令请带上域名参数！")
        return

    req = await session.get(f"https://namebeta.com/api/search/check?query={hostname}")

    if req.status_code == 200:
        try:
            data = (
                req.json()["whois"]["whois"].split("For more information")[0].rstrip()
            )
        except Exception:
            await message.edit_text("出错了呜呜呜 ~ 可能是域名不正确.")
            return
        await message.edit_text(f"<code>{data}</code>")
    else:
        await message.edit_text("出错了呜呜呜 ~ 无法访问到 API 服务器.")
