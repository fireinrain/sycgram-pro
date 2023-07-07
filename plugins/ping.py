from loguru import logger
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.helpers import Parameters, show_cmd_tip, show_exception
from tools.poster import check_ip, check_ip_port, process_check_data
from tools.sessions import session


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


@Client.on_message(command("ipcheck"))
async def ip_checker(_: Client, msg: Message):
    """检测IP或者域名是否被阻断"""
    cmd, args = Parameters.get_more(msg)
    if len(args) == 1:
        try:
            resp = await check_ip(args[0])
        except Exception as e:
            logger.error(e)
            return await show_exception(msg, e)
    elif len(args) == 2:
        try:
            resp = await check_ip_port(args[0], args[1])
        except Exception as e:
            logger.error(e)
            return await show_exception(msg, e)
    else:
        return await show_cmd_tip(msg, cmd)

    try:
        res = await process_check_data(len(args), resp=resp)
        await msg.edit_text(f"🔎 查询  `{' '.join(args)}`\n{res}")
    except Exception as e:
        logger.error(e)
        await show_exception(msg, e)
