import contextlib
import os
import secrets
from os import sep

from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters
from tools.sessions import session


async def get_wallpaper_url(num):
    json_url = f"https://www.bing.com/HPImageArchive.aspx?format=js&mkt=zh-CN&n=1&idx={str(num)}"
    req = await session.get(json_url, timeout=5.5)
    url = ""
    copy_right = ""
    if req.status_code == 200:
        data = req.json()
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
async def bingwall(message: Message):
    cmd, args = Parameters.get(message)
    status = False
    filename = f"data{sep}wallpaper.jpg"
    for _ in range(3):
        num = secrets.choice(range(7))
        url, copy_right = await get_wallpaper_url(num)
        image_url = f"https://www.bing.com{url}"
        try:
            if image_url != " ":
                img = await session.get(image_url, timeout=5.5)
            else:
                continue
            if img.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(img.content)
                if not args:
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
        except Exception as e:
            continue
    safe_remove(filename)
    if not status:
        return await message.edit_text("出错了😭😭😭 ~ 试了好多好多次都无法访问到服务器")
    await message.delete()


def safe_remove(name: str) -> None:
    with contextlib.suppress(FileNotFoundError):
        os.remove(name)
