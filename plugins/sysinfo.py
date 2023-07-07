from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.helpers import basher


@Client.on_message(command("sysinfo"))
async def sysinfo(_: Client, msg: Message):
    """查询系统信息"""
    res = await basher("neofetch --config none --stdout")
    if not res.get('error'):
        await msg.edit_text(f"```{res.get('output')}```")
    else:
        await msg.edit_text(f"```{res.get('error')}```")
