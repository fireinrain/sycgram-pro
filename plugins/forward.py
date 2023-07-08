from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import RPCError
from pyrogram.types import Message
from tools.helpers import Parameters, delete_this


async def check_replied_msg(msg: Message, cmd: str) -> bool:
    replied_msg = msg.reply_to_message
    if not replied_msg:
        await msg.edit_text(f"❗️ 请使用 `{cmd}` 回复一条消息。")
        return False
    elif replied_msg.has_protected_content or replied_msg.chat.has_protected_content:
        await msg.edit_text("😮‍💨 请不要转发受保护的消息！")
        return False
    else:
        return True


@Client.on_message(command('f'))
async def forward(_: Client, msg: Message):
    """转发目标消息"""
    cmd, num = Parameters.get_int(msg)
    replied_msg = msg.reply_to_message
    if not await check_replied_msg(msg, cmd):
        return

    await delete_this(msg)
    for _ in range(num):
        try:
            await replied_msg.forward(msg.chat.id, disable_notification=True)
        except RPCError as e:
            logger.error(e)


@Client.on_message(command('cp'))
async def copy_forward(cli: Client, msg: Message):
    """无引用转发"""
    cmd, num = Parameters.get_int(msg)
    if not await check_replied_msg(msg, cmd):
        return

    await delete_this(msg)
    for _ in range(num):
        try:
            await cli.copy_message(
                chat_id=msg.chat.id,
                from_chat_id=msg.chat.id,
                message_id=msg.reply_to_message.id,
                disable_notification=True
            )
        except RPCError as e:
            logger.error(e)
