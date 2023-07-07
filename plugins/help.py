from core import CMDS_DATA, command
from pyrogram import Client
from pyrogram.types import Message
from tools.helpers import Parameters
from pyrogram.enums import ParseMode 

@Client.on_message(command('help'))
async def helper(_: Client, msg: Message):
    """指令用法提示。格式：-help <cmd|None>"""
    helper_cmd, cmd = Parameters.get(msg)
    data = CMDS_DATA
    cmd_alias = dict(zip((v.get('cmd') for v in data.values()), data.keys()))
    if not cmd:
        tmp = '、'.join(f"`{k}`" for k in data.keys())
        text = f"📢 **指令列表：**\n{tmp}\n\n**发送** `{helper_cmd} " \
               f"<{cmd if cmd else 'cmd'}>` **查看某指令的详细用法**"
    elif not data.get(cmd) and cmd not in cmd_alias:
        text = f"❗️ Without this command >>> `{cmd}`"
    else:
        key = cmd if data.get(cmd) else cmd_alias.get(cmd)
        text = f"格式：`{data.get(key).get('format')}`\n" \
               f"用法：`{data.get(key).get('usage')}`"
    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
