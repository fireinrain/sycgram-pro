import asyncio
import re
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters, show_cmd_tip, show_exception
from typing import Any, Dict
from urllib import parse
from tools.sessions import session

from bs4 import BeautifulSoup
from loguru import logger

"""
data/command.yml

google:
  cmd: gg
  format: -gg <无|搜索内容>
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


async def google_search(content: str) -> Dict[str, str]:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip',
        'Accept-Language': 'zh,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,ja;q=0.6',
        'Referer': 'https://www.google.com/',
        'Sec-Ch-Ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'Sec-Ch-Ua-Arch': 'x86',
        'Sec-Ch-Ua-Bitness': '64',
        'Sec-Ch-Ua-Full-Version': '118.0.5993.88',
        'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="118.0.5993.88", "Google Chrome";v="118.0.5993.88", '
                                       '"Not=A?Brand";v="99.0.0.0"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Model': '""',
        'Sec-Ch-Ua-Platform': 'macOS',
        'Sec-Ch-Ua-Platform-Version': '12.5.1',
        'Sec-Ch-Ua-Wow64': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/118.0.0.0 Safari/537.36',
        'X-Client-Data': 'CJO2yQEIprbJAQipncoBCPDpygEIkqHLAQiGoM0BCMSxzQEI3L3NAQiRys0BCLnKzQEIzdDNAQjQ1s0BCPXWzQEIp9jNAQiY2c0BCOHazQEI5NrNAQiu280BCPnA1BUY9cnNARi50sB',
    }
    result: Dict[str, str] = {}
    url = f"https://www.google.com/search?q={parse.quote(content)}"
    async with session.get(url, headers=headers) as resp:
        if resp.status == 200:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            for p in soup.find_all('h3'):
                if p.parent.has_attr('href'):
                    result[p.text] = p.parent.attrs.get('href')
                    logger.info(f"Google | Searching | {result[p.text]}")
                    if len(result) > 10:
                        break
            return result

        resp.raise_for_status()
