import json
import time
from typing import Dict, Any
from urllib import parse

import aiohttp
import asyncio

from bs4 import BeautifulSoup
from googlesearch import search
from loguru import logger


async def fetch_json():
    pass


async def get_wallpaper_url(num) -> (str, str):
    async with aiohttp.ClientSession() as session:
        json_url = f"https://www.bing.com/HPImageArchive.aspx?format=js&mkt=zh-CN&n=1&idx={str(num)}"
        async with session.get(json_url) as response:
            url = ""
            copy_right = ""
            if response.status == 200:
                data = await response.json()
                url = data["images"][0]["url"]
                copy_right = data["images"][0]["copyright"]
            return url, copy_right


fakeopen_completions_url = 'https://ai.fakeopen.com/v1/chat/completions'


async def fakeopen_completions_chat(query: str, max: int, stream_true: bool, tem: float):
    params = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": "你好!"
            }
        ]
        ,
        'stream': True,
    }
    json_data = json.dumps(params)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJ3aW5reWVtZUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sImh0dHBzOi8vYXBpLm9wZW5haS5jb20vYXV0aCI6eyJwb2lkIjoib3JnLVhORjV1TEJ4MWlDaWNpVkJ1TkF4bVQxeiIsInVzZXJfaWQiOiJ1c2VyLTUxNThMejlyWHAyVThnVWhLcWRPWDNFdyJ9LCJpc3MiOiJodHRwczovL2F1dGgwLm9wZW5haS5jb20vIiwic3ViIjoiYXV0aDB8NjQ0MTJjYzZlYWJiNWY3OWU1NTM1MjczIiwiYXVkIjpbImh0dHBzOi8vYXBpLm9wZW5haS5jb20vdjEiLCJodHRwczovL29wZW5haS5vcGVuYWkuYXV0aDBhcHAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY5Nzg2MDg3OSwiZXhwIjoxNjk4NzI0ODc5LCJhenAiOiJUZEpJY2JlMTZXb1RIdE45NW55eXdoNUU0eU9vNkl0RyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgbW9kZWwucmVhZCBtb2RlbC5yZXF1ZXN0IG9yZ2FuaXphdGlvbi5yZWFkIG9yZ2FuaXphdGlvbi53cml0ZSBvZmZsaW5lX2FjY2VzcyJ9.nL_tj0Vh67PMwSlEzEP5LR5H438VITiiy-3MVD1boQt5rGgrrJofMvor8f9PxI4xA0RlqO6Ff5MEG0Blf-FDeLaQ2fI4qzeOE1KL1aWUBH_hprOwYFyg_cNFldmEen4jlL3oWBUC_35ggG3K-Zjac0oNa13u1bFdBZlwPcI0200qVztmqEovY8Ej9K7ZuH07rARPBbEvP-ixiN1UYpSCo_NTQM_xsT-nJM0IgnkuZUa-xnsyuJJQBxWe3pk1jib0UY-yltgVKi7ydbbtPstuUa1S31YsswsmKypQFCWXSqGVEQ46z0lAEir_85wnwosSdDtWhcsH0O5qxfJWfWJ3AQ',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/118.0.0.0 Safari/537.36'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(fakeopen_completions_url, data=json_data, headers=headers) as response:
            if response.status == 200:
                # 使用iter_any()方法逐块读取流式数据
                result = ""
                async for chunk in response.content.iter_any():
                    # 在这里处理每个数据块
                    print(chunk.decode("utf-8"))
                    decoded_chunk = chunk.decode("utf-8")
                    if 'choices' in decoded_chunk and 'delta' in decoded_chunk['choices'][0]:
                        chunk_msg = decoded_chunk['choices'][0]['delta'].get('content', '')
                        result += chunk_msg  # 将输出内容附加到结果字符串上

                        if stream_true:
                            # print(chunk_msg, end='', flush=True)
                            await asyncio.sleep(0.05)
                print(result)
                return result

            else:
                print(f"Failed to fetch data. Status code: {response.status}")
    return ""


async def execute(command: str) -> Dict[str, Any]:
    executor = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await executor.communicate()
    except Exception as e:
        return {'output': '', 'error': str(e)}
    else:
        return {
            'output': stdout.decode('utf-8', 'ignore').strip(),
            'error': stderr.decode('utf-8', 'ignore').strip()
        }


async def google_search(content: str) -> Dict[str, str]:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip',
        'Accept-Language': 'zh',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/118.0.0.0 Safari/537.36',

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
            continue

        resp.raise_for_status()


async def fetch_proxy_list() -> list[str]:
    url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=us&ssl=all&anonymity=all'
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


def google_search_with_lib(content: str) -> Dict[str, str]:
    g = search("Google", advanced=True, num_results=10)
    for item in g:
        print(item)


async def main():
    try:
        # res = await execute("whoami")
        # _output: str = res.get('output') if not res.get(
        #     'error') else res.get('error')
        # full_result = await fakeopen_completions_chat("你好", 5000, True, 0.8)

        # json_data = await get_wallpaper_url(1)
        # print(json_data)
        # print(_output)
        # proxy_list_ = await google_search("nihao")
        googlesearch1 = google_search_with_lib("x")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    asyncio.run(main())

    time.sleep(1000)
