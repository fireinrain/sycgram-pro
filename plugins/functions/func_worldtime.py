import asyncio
from datetime import datetime
from typing import Dict

import aiohttp
import pytz
from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters


async def get_world_time(timezone: str) -> Dict:
    if not timezone:
        timezone = pytz.timezone('Asia/Shanghai')
    url = f'https://worldtimeapi.org/api/timezone/{timezone}'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_data = None
                if response.status == 200:
                    response_data = await response.json()
                    wtr = response_data.get('datetime')
                    wtr_obj = datetime.strptime(wtr, "%Y-%m-%dT%H:%M:%S.%f%z")
                    time_24hr = wtr_obj.strftime("%H:%M:%S")
                    time_12hr = wtr_obj.strftime("%I:%M:%S %p")
                    return {'data': response_data, "result": "success", "24hr": time_24hr, "12hr": time_12hr}
                else:
                    return {'data': response_data, "result": "No result was found"}
    except Exception as e:
        return {"result": "An error occurred: " + str(e)}


@Client.on_message(command('wdtime'))
async def worldtime(client: Client, message: Message):
    """获取世界时间"""
    cmd, args = Parameters.get(message)
    await message.edit_text("🕐 正在查询所在时区时间,请稍后...")
    result = await get_world_time(args.strip())
    infos = (f"时区: `{result['data']['timezone']}/{result['data']['utc_offset']}`\n"
             f"星期: `{result['data']['day_of_week']}`\n"
             f"年中天数: `{result['data']['day_of_year']}`\n"
             f"当前时间: \n 12HR: `{result['12hr']}` \n 24HR: `{result['24hr']}`")
    if result['result'] == 'success':
        await message.edit_text(infos)
    else:
        await message.edit_text("查询失败!")
        await asyncio.sleep(5)
        await message.delete()
