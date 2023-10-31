import asyncio
import random
import re
import aiohttp
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters, show_cmd_tip, show_exception
from typing import Any, Dict
from urllib import parse

from bs4 import BeautifulSoup
from loguru import logger
from googlesearch import search

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
        # res = await google_search(pattern)
        res = google_search_with_lib(pattern)
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
        'User-Agent': get_useragent(),
    }
    session = aiohttp.ClientSession()
    # socks5
    proxy_ips = await fetch_proxy_list()
    for proxy in proxy_ips:
        result: Dict[str, str] = {}
        logger.info(f"当前使用http代理: {proxy}")
        url = f"https://www.google.com/search?q={parse.quote(content)}"
        try:
            async with session.get(url, headers=headers, proxy=f"http://{proxy}") as resp:
                if resp.status == 200:
                    soup = BeautifulSoup(await resp.text(), 'lxml')
                    for p in soup.find_all('h3'):
                        if p.parent.has_attr('href'):
                            result[p.text] = p.parent.attrs.get('href')
                            logger.info(f"Google | Searching | {result[p.text]}")
                            if len(result) > 10:
                                break
                    logger.info("使用代理访问google 成功！")
                    return result
        except Exception as e:
            logger.error(f"Google | Searching error: {e.message}")
            resp.close()
            continue

        resp.raise_for_status()


def google_search_with_lib(content: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    search_results = search(content, advanced=True, num_results=10)
    for item in search_results:
        result[item.title] = item.url
    return result


async def fetch_proxy_list() -> list[str]:
    url = ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=us&ssl=all'
           '&anonymity=all')
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                # Use the text() method to get the text content of the response
                text = await response.text()
                text = text.strip()
                split_ips = text.split("\r\n")
                return split_ips
            else:
                print(f"Request failed with status code: {response.status}")
                return None


def get_useragent():
    _useragent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
    ]
    return random.choice(_useragent_list)
