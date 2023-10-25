from loguru import logger
from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters, show_cmd_tip, show_exception
from tools.sessions import session
from typing import Any, Dict
import json

"""
data/command.yml

ip:
  cmd: ip
  format: -ip <IP地址|域名|me>
  usage: 查询IP地址或域名的信息
"""


# data = await requests.get(
#         f"http://ip-api.com/json/{url}?fields=status,message,country,regionName,"
#         f"city,lat,lon,isp,org,as,mobile,proxy,hosting,query"
# ) 获取更详细的信息
@Client.on_message(command('ip'))
async def ip(_: Client, msg: Message):
    """查询ip信息"""
    cmd, address = Parameters.get(msg)
    if not address:
        return await show_cmd_tip(msg, cmd)
    elif address == "me":
        address = ''

    async def get_api(api: str) -> str:
        async with session.get(api) as resp:
            if resp.status == 200:
                data = await resp.json()
                tmp = '\n'.join(f"{k}：`{v}`" for k, v in data.items())
                return tmp if tmp else "😂 没有响应 ~"
            resp.raise_for_status()

    try:
        api = f"http://ip-api.com/json/{address}"
        text = await get_api(api)
    except Exception as e:
        return await show_exception(msg, e)
    else:
        await msg.edit_text(text)


"""
data/command.yml

ipcheck:
  cmd: ipc
  format: -ipcheck <IP|域名> <端口|无>
  usage: 无端口参数时，查询IP或域名是否被阻断；有则查询端口是否开启
"""


@Client.on_message(command("ipcheck"))
async def ip_checker(_: Client, msg: Message):
    """检测IP或者域名是否被阻断"""
    cmd, args = Parameters.get_more(msg)
    args_size = len(args)
    if args_size == 1:
        try:
            resp = await check_ip(args[0])
        except Exception as e:
            logger.error(e)
            return await show_exception(msg, e)
    elif args_size == 2:
        try:
            resp = await check_ip_port(args[0], args[1])
        except Exception as e:
            logger.error(e)
            return await show_exception(msg, e)
    else:
        return await show_cmd_tip(msg, cmd)

    try:
        res = await process_check_data(args_size, resp=resp)
        await msg.edit_text(f"🔎 查询  `{' '.join(args)}`\n{res}")
    except Exception as e:
        logger.error(e)
        await show_exception(msg, e)


# {'icmp': 'fail', 'tcp': 'fail', 'outside_tcp': 'fail', 'outside_icmp': 'success'}
#  asyncio.run(check_ip_port('8.8.8.8', '22'))
# {'icmp': 'success', 'tcp': 'fail'}
# asyncio.run(check_ip('8.8.8.8'))

async def check_ip(ip: str) -> Dict[str, Any]:
    # ------------- ip check --------------
    # set check port as 80 as default
    result = await check_ip_port(ip, '80')
    return result


async def check_ip_port(ip: str, port: str) -> Dict[str, str]:
    # ------------- ip check --------------
    url = "https://www.toolsdaquan.com/toolapi/public/ipchecking"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,ja;q=0.6",
        # "Cookie": "_ga=GA1.1.251509313.1693217699; Hm_lvt_6c497f74830b2047430c4a193e515dde=1693526274; Hm_lpvt_6c497f74830b2047430c4a193e515dde=1693527480; _ga_68FZ9NYKJ7=GS1.1.1698223819.8.0.1698223819.0.0.0",
        "Referer": "https://www.toolsdaquan.com/ipcheck/",
        "Sec-Ch-Ua": "\"Chromium\";v=\"118\", \"Google Chrome\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
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
            inner_data.update({'ip': f'{ip}', 'port': f'{port}'})
        else:
            resp.raise_for_status()
    return inner_data


async def process_check_data(opt: int, resp: Dict[str, Any]) -> str:
    # 检测ip
    if opt == 1:
        _data = resp
        in_icmp = "✅" if _data.get('icmp') == 'success' else "❌"
        in_tcp = "✅" if _data.get('tcp') == 'success' else "❌"
        out_icmp = "✅" if _data.get('outside_icmp') == 'success' else "❌"
        out_tcp = "✅" if _data.get('outside_tcp') == 'success' else "❌"
        return f"```ICMP：{in_icmp}\n" \
               f"TCP： {in_tcp}\n" \
               f"Outside ICMP：{out_icmp}\n" \
               f"Outside TCP： {out_tcp}```"

    # 检测ip端口
    elif opt == 2:
        _data = resp
        in_icmp = "✅" if _data.get('icmp') == 'success' else "❌"
        in_tcp = "✅" if _data.get('tcp') == 'success' else "❌"
        out_icmp = "✅" if _data.get('outside_icmp') == 'success' else "❌"
        out_tcp = "✅" if _data.get('outside_tcp') == 'success' else "❌"
        return f"```ICMP：{in_icmp}\n" \
               f"TCP： {in_tcp}\n" \
               f"Outside ICMP：{out_icmp}\n" \
               f"Outside TCP： {out_tcp}```"
