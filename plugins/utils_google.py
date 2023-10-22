import asyncio
import re

from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from tools.poster import google_search
from tools.helpers import Parameters, show_cmd_tip, show_exception
from pyrogram.enums import ParseMode

"""
data/command.yml

google:
  cmd: g
  format: -google <无|搜索内容>
  usage: 回复一条消息，或直接使用
"""


@Client.on_message(command("google"))
async def google(_: Client, msg: Message):
    """谷歌搜索并展示第一页结果和链接"""
    cmd, args = Parameters.get(msg)
    replied_msg = msg.reply_to_message
    if not args and replied_msg and (replied_msg.text or replied_msg.caption):
        pattern = replied_msg.text or replied_msg.caption
    elif args:
        pattern = args
    else:
        return await show_cmd_tip(msg, cmd)

    try:
        res = await google_search(pattern)
        links = '\n\n'.join(
            f"[{title[0:30]}]({url})" for title, url in res.items()
        )
        pattern = re.sub(r'[_*`[]', '', pattern[0:30])
        text = f"🔎 | **谷歌搜索结果** | `{pattern}`\n{links}"
        await msg.edit_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await msg.edit_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(e)
        await show_exception(msg, "无法连接到谷歌")
    finally:
        await logger.complete()
