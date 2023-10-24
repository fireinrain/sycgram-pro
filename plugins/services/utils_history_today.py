from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.sessions import session


async def get_history_today_info() -> str:
    """
    获取历史上的今天，并格式化输出
    """
    pass


"""
data/command.yml

histoday:
  cmd: histd
  format: -histd <无>
  usage: 生成历史上的今天摘要
"""


@Client.on_message(command('histoday'))
async def dictionary(_: Client, msg: Message):
    """历史上的今天"""
    api_url = "https://www.ipip5.com/today/api.php?type=json"

    # with session.get()
    #
    # await msg.edit_text(f"正在准备{}。")
    pass
