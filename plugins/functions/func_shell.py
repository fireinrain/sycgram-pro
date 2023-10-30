import asyncio
from getpass import getuser
from io import BytesIO
from platform import node

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters, basher, delete_this, show_cmd_tip, show_exception

"""
data/command.yml

shell:
  cmd: sh
  format: -sh <shell脚本>
  usage: 直接使用
"""


@Client.on_message(command("shell"))
async def shell(_: Client, msg: Message):
    """执行shell脚本"""
    cmd, _input = Parameters.get(msg)
    if not _input:
        return await show_cmd_tip(msg, cmd)

    try:
        res = await basher(_input, timeout=30)
    except asyncio.exceptions.TimeoutError:
        return await show_exception(msg, "连接超时！")

    _output: str = res.get('output') if not res.get(
        'error') else res.get('error')
    header = f"**{getuser()}@{node()}**\n"
    all_bytes = len(header.encode() + _input.encode() + _output.encode())
    if all_bytes >= 2048:
        await delete_this(msg)
        return await msg.reply_document(
            document=BytesIO(_output.encode()),
            caption=f"{header}> # `{_input}`",
            file_name="output.log",
            parse_mode=ParseMode.MARKDOWN
        )

    await msg.edit_text(
        f"{header}> # `{_input}`\n```bash\n{_output.strip()}```",
        parse_mode=ParseMode.MARKDOWN
    )
