import asyncio
import time
from typing import List

from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message
from tools.helpers import Parameters, get_iterlimit, is_deleted_id


@Client.on_message(command('dme'))
async def dme(client: Client, message: Message):
    """删除指令数量的消息"""
    cmd, limit = Parameters.get_int(message, max_num=1500)
    counter, ids_deleted = 0, []
    await message.edit_text("🧹`正在删除历史消息...`")
    start = time.time()

    async def delete_messages(cli: Client, ids_deleted: List[int]):
        if len(ids_deleted) == 100:
            try:
                await cli.delete_messages(message.chat.id, ids_deleted)
            except FloodWait as e:
                await asyncio.sleep(e.x + 0.5)
            except RPCError as e:
                logger.error(e)
            else:
                ids_deleted.clear()

    # 第一阶段，暴力扫描最近的消息，这些消息有可能无法搜索到
    async for msg in client.get_chat_history(message.chat.id, limit=get_iterlimit(limit)):
        if is_deleted_id(msg):
            logger.info(f'{cmd} | scanning | {msg.id}')
            ids_deleted.append(msg.id)
            counter = counter + 1
            await delete_messages(client, ids_deleted)
            if counter == limit:
                break

    # 第二阶段，对于老的消息直接扫描性能不好，还会触发限制，使用搜索功能来提速
    if counter < limit:
        async for msg in client.search_messages(
            chat_id=message.chat.id,
            offset=counter,
            limit=limit - counter,
            from_user='me',
        ):
            if is_deleted_id(msg) and msg.id not in ids_deleted:
                logger.info(f'{cmd} | searching | {msg.id}')
                ids_deleted.append(msg.id)
                counter = counter + 1
                await delete_messages(client, ids_deleted)
                if counter == limit:
                    break

    if len(ids_deleted) != 0:
        await client.delete_messages(message.chat.id, ids_deleted)
    text = f"🧹删除 {counter} 条消息使用了 {time.time() - start:.3f} 秒。"
    res = await message.reply(text)
    await asyncio.sleep(3)
    await res.delete()
    # log
    logger.success(f"{cmd} | {text}")
    await logger.complete()
