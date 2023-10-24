from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import get_fullname

"""
data/command.yml

idme:
  cmd: idme
  format: -idme
  usage: 回复一条消息或直接使用，查看对话及消息的ID
"""


@Client.on_message(command("idme"))
async def get_id(_: Client, msg: Message):
    """直接使用或者回复目标消息，从而获取各种IDs"""
    text = f"消息ID: `{msg.id}`\n\n" \
           f"群聊标题: `{msg.chat.title or msg.chat.first_name}`\n" \
           f"群聊类型: `{msg.chat.type}`\n" \
           f"群聊ID: `{msg.chat.id}`"

    replied_msg = msg.reply_to_message
    if replied_msg and replied_msg.from_user:
        user = replied_msg.from_user
        text = f"回复消息ID: `{replied_msg.id}`\n\n" \
               f"用户昵称: `{get_fullname(user)}`\n" \
               f"用户名: `@{user.username}`\n" \
               f"用户ID: `{user.id}`\n\n" \
               f"{text}"
    elif replied_msg and replied_msg.sender_chat:
        sender_chat = replied_msg.sender_chat
        text = f"回复消息ID: `{replied_msg.id}`\n\n" \
               f"群聊标题: `{sender_chat.title}`\n" \
               f"消息类型: `{sender_chat.type}`\n" \
               f"群聊ID: `{sender_chat.id}`\n\n" \
               f"{text}"

    await msg.edit_text(text)
