import json
from time import time
from typing import Any, Dict
from urllib import parse

from bs4 import BeautifulSoup
from loguru import logger

from .sessions import session


async def google_search(content: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    async with session.get(
        f"https://www.google.com/search?q={parse.quote(content)}", timeout=9.9
    ) as resp:
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


async def check_ip(ip: str) -> Dict[str, Any]:
    # ------------- ip check --------------
    url = "https://www.vps234.com"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        'origin': url,
        'referer': f'{url}/ipchecker/',
        'x-requested-with': 'XMLHttpRequest'
    }

    async with session.post(
        f"{url}/ipcheck/getdata/",
        data={
            'idName': f'itemblockid{int(round(time() * 1000))}',
            'ip': ip,
        },
        headers=headers
    ) as resp:
        if resp.status == 200:
            return await resp.json()

        resp.raise_for_status()


async def check_ip_port(ip: str, port: str) -> Dict[str, str]:
    # ------------- ip check --------------
    url = "https://www.toolsdaquan.com/toolapi/public/ipchecking"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        'referer': 'https://www.toolsdaquan.com/ipcheck/',
        'x-requested-with': 'XMLHttpRequest'
    }

    async with session.post(f"{url}/{ip}/{port}", headers=headers) as resp:
        if resp.status == 200:
            # inner_data = await resp.json()
            inner_data = json.loads(await resp.text())
        else:
            resp.raise_for_status()

    async with session.post(f"{url}2/{ip}/{port}", headers=headers) as resp:
        if resp.status == 200:
            # outer_data = await resp.json()
            outer_data = json.loads(await resp.text())
            inner_data.update(outer_data)
        else:
            resp.raise_for_status()
    return inner_data


async def process_check_data(opt: int, resp: Dict[str, Any]) -> str:
    print(resp)

    if opt == 1:
        data = resp.get('data')
        if resp.get('error') or not data.get('success'):
            return f"⚠️ Api Connection failed. Message is `{resp.get('msg')}`"
        _data = data.get('data')
        in_icmp = "✅" if _data.get('innerICMP') else "❌"
        in_tcp = "✅" if _data.get('innerTCP') else "❌"
        out_icmp = "✅" if _data.get('outICMP') else "❌"
        out_tcp = "✅" if _data.get('outTCP') else "❌"
        return f"```Inner ICMP：{in_icmp}\n" \
               f"Inner TCP： {in_tcp}\n" \
               f"Outer ICMP：{out_icmp}\n" \
               f"Outer TCP： {out_tcp}```"

    elif opt == 2:
        def is_opened(key):
            return resp.get(key) == 'success'

        in_icmp = "✅" if is_opened('icmp') else "❌"
        in_tcp = "✅" if is_opened('tcp') else "❌"
        out_icmp = "✅" if is_opened('outside_icmp') else "❌"
        out_tcp = "✅" if is_opened('outside_tcp') else "❌"
        return f"```Inner ICMP：{in_icmp}\n" \
               f"Inner TCP： {in_tcp}\n" \
               f"Outer ICMP：{out_icmp}\n" \
               f"Outer TCP： {out_tcp}```"
