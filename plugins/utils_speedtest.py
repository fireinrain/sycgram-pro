import asyncio
import re

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from core import command
from tools.constants import SPEEDTEST_RUN, SYCGRAM_INFO
from tools.helpers import Parameters, delete_this, show_cmd_tip, show_exception
from tools.speedtests import Speedtester

"""
data/command.yml

speedtest:
  cmd: c
  format: -speedtest <无|节点ID|list|update>
  usage: 服务器本地网络测速
"""


@Client.on_message(command('speedtest'))
async def speedtest(_: Client, msg: Message):
    """服务器测速，用法：-speedtest <节点ID|list|update>"""
    cmd, opt = Parameters.get(msg)

    await msg.edit_text("⚡️ Speedtest正在测速，请稍后...")
    async with Speedtester() as tester:
        if opt == 'update':
            try:
                update_res = await tester.install_speedtest_cli('update')
            except asyncio.exceptions.TimeoutError:
                await show_exception(msg, "更新超时！")
            except Exception as e:
                await show_exception(msg, e)
            else:
                await msg.edit_text(
                    f"**{SYCGRAM_INFO}**\n> # `{update_res}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            return
        elif opt == 'list':
            try:
                text = await tester.list_servers_ids(f"{SPEEDTEST_RUN} -L")
                await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
            except asyncio.exceptions.TimeoutError:
                await show_exception(msg, "测速超时")
            except Exception as e:
                await show_exception(msg, e)
            return
        elif bool(re.match(r'[0-9]+', opt)) or not opt:
            try:
                text, link = await tester.running(
                    f"""{SPEEDTEST_RUN}{'' if not opt else f' -s {opt}'}"""
                )
            except asyncio.exceptions.TimeoutError:
                return await show_exception(msg, "测速超时")
        else:
            return await show_cmd_tip(msg, cmd)
    await delete_this(msg)
    if not link:
        return await msg.edit_text(text)

    # send speed report
    try:
        await msg.reply_photo(photo=link, caption=text, parse_mode=ParseMode.MARKDOWN)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await msg.reply_photo(photo=link, caption=text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await show_exception(msg, e)


def unit_convert(byte):
    """Converts byte into readable formats."""
    power = 1024
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while byte > power:
        byte /= power
        zero += 1
    return f"{round(byte, 2)} {units[zero]}"
