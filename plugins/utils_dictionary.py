from pyrogram import Client
from pyrogram.types import Message

from core import command

"""
data/command.yml

dictionary:
  cmd: dic
  format: dic <enzh|zhen> <text>
  usage: 在线英汉-汉英字典服务
"""


@Client.on_message(command('dictionary'))
async def dictionary(_: Client, msg: Message):
    """肯德基"""
    symbol = 'vm50ing... '
    api = 'https://kfc-crazy-thursday.vercel.app/api/index'
    await msg.edit_text(f"正在准备{symbol}。")
