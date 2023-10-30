import contextlib
import os
import random
import string
from typing import Dict

import aiofiles
import aiohttp
import requests
from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters


# 备用api
# https://api.screenshotmachine.com?
# key=your_key
# &url=v2ph.com
# &device=desktop
# &dimension=1024x768
# &format=jpg
# &cacheLimit=0
# &delay=3000

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def fetch_webshot_image(site_url: str) -> Dict:
    if "http://" not in site_url and "https://" not in site_url:
        site_url = "https://" + site_url
        code = requests.get(site_url).status_code
        if code != 200:
            site_url = site_url.replace("https://", "https://")
    try:
        image_url = f'https://image.thum.io/get/maxAge/12/width/720/{site_url}'

        # Create a session to manage connections
        async with aiohttp.ClientSession() as session:
            # Preload URL first
            async with session.get(image_url) as preload_response:
                pass

            # Download the actual image
            async with session.get(image_url, timeout=30) as response:
                if response.status == 200:
                    if not os.path.exists("uploads/webshot"):
                        os.makedirs("uploads/webshot")

                    image_file_path = os.path.join("uploads/webshot", f"{generate_random_string(15)}.png")

                    async with aiofiles.open(image_file_path, "wb") as f:
                        await f.write(await response.read())

                    return {
                        'direct_result': {
                            'kind': 'photo',
                            'format': 'path',
                            'value': image_file_path
                        }
                    }
                else:
                    return {'result': 'Unable to screenshot website'}
    except Exception as e:
        if 'image_file_path' in locals() and os.path.exists(image_file_path):
            os.remove(image_file_path)
        raise e  # You might want to handle or log the exception here


@Client.on_message(command("webshot"))
async def webshot(client: Client, msg: Message):
    """获取网页截图"""
    cmd, args = Parameters.get(msg)
    await msg.edit_text("📷正在获取网页截图,请稍等...")

    data_dict = await fetch_webshot_image(args.strip())
    image_path = data_dict['direct_result']['value']
    await msg.reply_photo(
        image_path,
        caption=f"#webshot\n `{args.strip()}`",
        quote=False,
        reply_to_message_id=msg.reply_to_top_message_id,
    )
    safe_remove(image_path)

    await msg.delete()


def safe_remove(name: str) -> None:
    with contextlib.suppress(FileNotFoundError):
        os.remove(name)
