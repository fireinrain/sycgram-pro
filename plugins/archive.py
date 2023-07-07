import asyncio
from core import command
from pyrogram import Client
from pyrogram.types import Message


@Client.on_message(command("archive"))
async def archive(cli: Client, msg: Message):
    if await cli.archive_chats(msg.chat.id):
        await msg.edit_text(f"✅ 归档 `{msg.chat.title}` 成功")
    else:
        await msg.edit_text(f"❌ 归档失败 `{msg.chat.title}`！")
    await asyncio.sleep(2)
    await msg.delete()


@Client.on_message(command("unarchive"))
async def unarchive(cli: Client, msg: Message):
    if await cli.unarchive_chats(msg.chat.id):
        await msg.edit_text(f"✅ 取消归档 `{msg.chat.title}` 成功")
    else:
        await msg.edit_text(f"❌ 取消归档失败 `{msg.chat.title}`！")
    await asyncio.sleep(2)
    await msg.delete()
