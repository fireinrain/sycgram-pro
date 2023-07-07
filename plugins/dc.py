from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.helpers import get_dc_text
from pyrogram.enums import ParseMode 

@Client.on_message(command('dc'))
async def dc(_: Client, msg: Message):
    """获取群聊或者目标消息用户的dc_id"""
    _is_replied = bool(msg.reply_to_message)
    dc_id = msg.reply_to_message.from_user.dc_id \
        if _is_replied else msg.chat.dc_id
    name = msg.reply_to_message.from_user.mention(style=ParseMode.MARKDOWN) \
        if _is_replied else f"`{msg.chat.title or msg.chat.first_name}`"
    await msg.edit_text(get_dc_text(name, dc_id))
