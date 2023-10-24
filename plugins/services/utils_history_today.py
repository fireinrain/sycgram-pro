from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from core import command
from tools.sessions import session


async def get_history_today_info(api_url: str) -> str:
    """
    获取历史上的今天，并格式化输出
    """
    async with session.get(api_url) as response:
        if response.status == 200:
            data = await response.json()
            data_list = data['result'][:-1]
            google_search = f"https://www.google.com/search?q="
            markdown_list = [f"[{item['year']}年 {item['title']}]({google_search + item['title']})" for item in
                             data_list]
            md = "\n".join(markdown_list)
            result = f"📅 | **历史上的今天** | `{data['today']}`\n{md}"
            return result
        else:
            raise Exception(f"HTTP request failed with status code {response.status}")


"""
data/command.yml

histoday:
  cmd: histd
  format: -histd <无>
  usage: 生成历史上的今天摘要
"""


@Client.on_message(command('histoday'))
async def dictionary(_: Client, msg: Message):
    """历史上的今天"""
    api_url = "https://www.ipip5.com/today/api.php?type=json"
    try:
        data = await get_history_today_info(api_url)
        await msg.edit_text(
            text=data,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    except Exception as e:
        await msg.edit_text(f"api获取数据失败: {e.message}")
