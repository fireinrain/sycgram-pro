import asyncio

from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message
from tools.helpers import delete_this, escape_markdown
from tools.sessions import session
from pyrogram.enums import ParseMode 

@Client.on_message(command("diss"))
async def diss(_: Client, msg: Message):
    """喷人"""
    symbol = '💢 '
    api = 'https://zuan.shabi.workers.dev/'
    await msg.edit_text(f"{symbol}正在准备开喷.")
    await get_api(api=api, msg=msg)


@Client.on_message(command('tg'))
async def tg(_: Client, msg: Message):
    """舔狗"""
    symbol = '👅 '
    # api = 'http://ovooa.com/API/tgrj/api.php'
    api='https://www.xzccc.com/api/dog/'
    await msg.edit_text(f"{symbol}正在准备开舔.")
    await get_api(api=api, msg=msg)

@Client.on_message(command('kfc'))
async def kfc(_: Client, msg: Message):
    """肯德基"""
    symbol = 'vm50ing... '
    api='https://kfc-crazy-thursday.vercel.app/api/index'
    await msg.edit_text(f"{symbol}正在准备.")
    await get_api(api=api, msg=msg)

async def get_api(api: str, msg: Message) -> None:
    for _ in range(10):
        try:
            resp = await session.get(api, timeout=5.5)
            if resp.status == 200:
                text = escape_markdown(await resp.text())
            else:
                resp.raise_for_status()
        except Exception as e:
            logger.error(e)
            continue
        words = f"{msg.reply_to_message.from_user.mention(style=ParseMode.MARKDOWN)} {text}" \
            if msg.reply_to_message and msg.reply_to_message.from_user else text
        try:
            await msg.edit_text(words, parse_mode=ParseMode.MARKDOWN)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await msg.edit_text(words, parse_mode=ParseMode.MARKDOWN)
        except RPCError as e:
            logger.error(e)
        await logger.complete()
        return
    # Failed to get api text
    await delete_this(msg)
    res = await msg.edit_text('😤 休息一下.')
    await asyncio.sleep(3)
    await delete_this(res)
