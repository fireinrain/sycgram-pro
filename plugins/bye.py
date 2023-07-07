from core import CMDS_PREFIX, command
from loguru import logger
from pyrogram import Client
from pyrogram.types import Message
from tools.constants import TG_GROUPS


@Client.on_message(command("bye"))
async def calculate(client: Client, msg: Message):
    # 仅销毁私人聊天，凑合用用，其他细节请自行补充
    if msg.chat.type in TG_GROUPS:
        return await msg.delete()
    elif msg.text != f'{CMDS_PREFIX}bye true':
        return await msg.delete()

    await msg.edit_text(text="即将销毁当前对话。。。")
    cid = msg.chat.id
    logger.info(f"This chat_id is {cid}")

    # msg_ids = []
    await client.delete_messages(chat_id=cid, message_ids=[
        message.id async for message in client.get_chat_history(cid)
    ])
    await msg.chat.archive()
