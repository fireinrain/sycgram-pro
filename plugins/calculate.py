import asyncio

from core import command
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message
from tools.helpers import Parameters, basher, show_exception


@Client.on_message(command("cal"))
async def calculate(_: Client, msg: Message):
    """计算器"""
    _, args = Parameters.get(msg)
    try:
        res = await basher(f"""echo "scale=4;{args}" | bc""", 3)
    except asyncio.exceptions.TimeoutError:
        return await show_exception(msg, "Connection Timeout！")
    if not res.get('output'):
        await msg.edit_text(f"Error：{res.get('error')}")
        return

    text = f"""In：`{args}`\nOut：`{res.get('output')}`"""
    try:
        await msg.edit_text(text)
    except FloodWait as e:
        await asyncio.sleep(e.x)
    except RPCError:
        await msg.edit_text(text)
