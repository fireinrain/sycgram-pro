from base64 import b64decode, b64encode

from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters

"""
data/command.yml

base64:
  cmd: base64
  format: base64 <e|d> text
  usage: 使用base64 编解码文字内容
"""


@Client.on_message(command("base64"))
async def base64(_: Client, message: Message):
    cmd, args = Parameters.get(message)
    msg = args
    if not msg:
        return await message.edit_text("`出错了呜呜呜 ~ 无效的参数。`")
    args_list = args.split(" ")
    subcmd = args_list[0].strip()
    msg = args_list[1].strip()
    if subcmd == "e":
        if result := b64encode(msg.encode("utf-8")).decode("utf-8"):
            await message.edit_text(f"`{result}`")
    if subcmd == "d":
        try:
            result = b64decode(msg).decode("utf-8")
        except Exception as e:
            return await message.edit_text("`出错了呜呜呜 ~ 无效的参数。`")
        if result:
            await message.edit_text(f"`{result}`")
