# ip 回程路由测试
from pyrogram import Client
from pyrogram.types import Message

from core import command

"""
data/command.yml


iptrace:
  cmd: iptrace
  format: -iptrace <back/best>
  usage: 主机回程路由测试(back 运行backtrace,best 运行besttrace)
"""


@Client.on_message(command('iptrace'))
async def dictionary(_: Client, msg: Message):
    """主机回程线路测试"""
    await msg.edit_text(f"当前功能正在施工🚧中,请耐心等待插件上线")
    # TODO finish me
