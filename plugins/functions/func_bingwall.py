import asyncio
import contextlib
import os
import secrets
from os import sep
import aiofiles
from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters
from tools.sessions import session


async def get_wallpaper_url(num) -> (str, str):
    json_url = f"https://www.bing.com/HPImageArchive.aspx?format=js&mkt=zh-CN&n=1&idx={str(num)}"
    async with session.get(json_url) as response:
        url = ""
        copy_right = ""
        if response.status == 200:
            data = await response.json()
            url = data["images"][0]["url"]
            copy_right = data["images"][0]["copyright"]
        return url, copy_right


"""
data/command.yml

ingwall:
  cmd: bgw
  format: -bgw <无|o>
  usage: 每日bing wallpaper壁纸,o参数发送原图
"""


@Client.on_message(command("bingwall"))
async def bingwall(client: Client, message: Message):
    await message.edit_text("🖼 正在获取每日bing壁纸...")
    cmd, args = Parameters.get(message)
    status = False
    filename = f"data{sep}wallpaper.jpg"
    for _ in range(3):
        num = secrets.choice(range(7))
        url, copy_right = await get_wallpaper_url(num)
        image_url = f"https://www.bing.com{url}"
        try:
            if image_url != " ":
                async with session.get(image_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(filename, mode='wb') as file:
                            while True:
                                chunk = await response.content.read(1024)
                                if not chunk:
                                    break
                                await file.write(chunk)
                        if args == "o":
                            await message.reply_document(
                                filename,
                                caption=f"#bing wallpaper\n" f"{str(copy_right)}",
                                quote=False,
                                reply_to_message_id=message.reply_to_top_message_id,
                            )
                        else:
                            await message.reply_photo(
                                filename,
                                caption=f"#bing wallpaper\n" f"{str(copy_right)}",
                                quote=False,
                                reply_to_message_id=message.reply_to_top_message_id,
                            )
                        status = True
                        break  # 成功了就赶紧结束啦！
            else:
                continue

        except Exception as e:
            continue
    safe_remove(filename)
    if not status:
        await message.edit_text("出错了😭😭😭 ~ 试了好多好多次都无法访问到服务器")
        await asyncio.sleep(5)
    await message.delete()


def safe_remove(name: str) -> None:
    with contextlib.suppress(FileNotFoundError):
        os.remove(name)
