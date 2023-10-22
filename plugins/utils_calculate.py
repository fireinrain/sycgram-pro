import asyncio

from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters, basher, show_exception

"""
data/command.yml

cal:
  cmd: cal
  format: -cal <四则运算式|^|sqrt()>
  usage: 直接使用。默认除法精确到小数点后4位
"""


@Client.on_message(command("cal"))
async def calculate(_: Client, msg: Message):
    """计算器"""
    _, args = Parameters.get(msg)
    try:
        res = await basher(f"""echo "scale=4;{args}" | bc""", 3)
    except asyncio.exceptions.TimeoutError:
        return await show_exception(msg, "连接超时！")
    if not res.get('output'):
        await msg.edit_text(f"Error：{res.get('error')}")
        return

    text = f"""输入：`{args}`\n输出：`{res.get('output')}`"""
    try:
        await msg.edit_text(text)
    except FloodWait as e:
        await asyncio.sleep(e.x)
    except RPCError:
        await msg.edit_text(text)


@Client.on_message(command("basecon"))
async def con(_: Client, message: Message):
    cmd, args = Parameters.get(message)
    subcmd = args.split(" ")
    if not subcmd:
        await message.edit_text("`出错了呜呜呜 ~ 无效的参数。`")
        return

    obase = subcmd[0].upper().strip()
    num = subcmd[1].upper().strip()
    await message.edit_text(f"{num}")
    cmd = f'echo "obase={obase};{num}" | bc'
    result = await basher(cmd)

    if result:
        await message.edit_text(f"{num}=\n`{result}`\n{obase}进制")
        return
    else:
        await message.edit_text(f"{num}->{obase}进制转换失败!")
        return
