from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import basher

"""
data/command.yml

sysinfo:
  cmd: sys
  format: -sys
  usage: 直接使用，查看当前运行环境系统信息
"""


@Client.on_message(command("sysinfo"))
async def sysinfo(_: Client, msg: Message):
    """查询当前运行环境系统信息"""
    res = await basher("neofetch --config none --stdout")
    if not res.get('error'):
        await msg.edit_text(f"```{res.get('output')}```")
    else:
        await msg.edit_text(f"```{res.get('error')}```")
