import asyncio

from core.custom import command
from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message
from tools.constants import STORE_GHOST_DATA, TG_PRIVATE
from tools.ghosts import get_ghost_to_read
from tools.helpers import (Parameters, delete_this, get_fullname,
                           get_sender_name)
from tools.storage import SimpleStore
from pyrogram.enums import ParseMode 


@Client.on_message(filters.incoming, group=-2)
async def ghost_event(cli: Client, msg: Message):
    """自动标记对话为<已读>"""
    if await get_ghost_to_read(msg.chat.id):
        try:
            await cli.get_chat_history(msg.chat.id)
        except RPCError as e:
            logger.error(e)
        else:
            if msg.text or msg.caption:
                chat_name = msg.chat.title or TG_PRIVATE
                sender_name = get_sender_name(msg)
                text = msg.text or msg.caption
                text = f"Ghost | {chat_name} | {sender_name} | {text}"
                logger.debug(text)
        finally:
            await logger.complete()


@Client.on_message(command('ghost'))
async def ghost(_: Client, msg: Message):
    """指令：将该对话标记为可自动<已读>状态"""
    _, opt = Parameters.get(msg)
    chat = msg.chat

    async with SimpleStore(auto_flush=False) as store:
        ghost_data = store.get_data(STORE_GHOST_DATA)
        # ghost状态
        if opt == 'status':
            text = f"此对话是否开启ghost：{'✅' if chat.id in ghost_data else '❌'}"
        elif opt == 'list':
            tmp = '\n'.join(f'```{k} {v}```' for k, v in ghost_data.items())
            text = f"📢 已开启ghost的对话名单：\n{tmp}"
        # ghost开关
        else:
            if chat.id in ghost_data:
                text = "❌ 已关闭此对话的ghost"
                ghost_data.pop(chat.id, None)
            else:
                text = "✅ 已开启此对话的ghost"
                ghost_data[chat.id] = chat.title or get_fullname(msg.from_user)
            store.flush()

    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    await asyncio.sleep(1)
    if opt != 'status' and opt != 'list':
        await delete_this(msg)
