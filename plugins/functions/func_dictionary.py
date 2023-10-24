from pyrogram import Client
from pyrogram.types import Message

from core import command

"""
data/command.yml

dictionary:
  cmd: dict
  format: -dict <enzh|zhen> <单词或文字>
  usage: 在线英汉-汉英字典服务
"""


@Client.on_message(command('dictionary'))
async def dictionary(_: Client, msg: Message):
    """英汉汉英字典查询"""
    await msg.edit_text(f"当前功能正在施工🚧中,请耐心等待插件上线")
    # TODO finish me
