import urllib.parse

from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters

"""
data/command.yml

jupai:
  cmd: jupai
  format: -jupai <文本>
  usage: 输入文字生成举牌小人图
"""


@Client.on_message(command("jupai"))
async def ju_pai_image(client: Client, message: Message):
    ju_pai_api = "https://api.txqq.pro/api/zt.php"
    cmd, args = Parameters.get(message)
    text = args
    if not args:
        return await message.edit_text(f"请输入需要举牌的文字信息!")
    try:
        image_url = f"{ju_pai_api}?msg={urllib.parse.quote(text)}"
        await message.reply_photo(
            image_url,
            quote=False,
            reply_to_message_id=message.reply_to_message_id
                                or message.reply_to_top_message_id,
        )
        await message.delete()
    except Exception as e:
        await message.edit_text(f"获取举牌小人图片失败😭😭😭")
