import html
import re

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters
from tools.sessions import session


# 清理html
def clean_html(raw_html):
    return re.sub(re.compile(r"<.*?>"), "", raw_html)


# 保护HTML文档中的数据，确保其中的字符串不会破坏HTML结构或引发潜在的安全性问题
def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(clean_html(value))
    return definition


@Client.on_message(command("pypi"))
async def pypi_search(client: Client, message: Message):
    cmd, args = Parameters.get(message)
    if not args:
        await message.edit_text("请输入包名关键字!")
        return
    r = await session.get(
        f"https://pypi.org/pypi/{message.arguments}/json", follow_redirects=True
    )
    if r.status != 200:
        await message.edit_text("无法搜索到相关包信息")
        return
    json = r.json()
    pypi_info = escape_definition(json["info"])
    text = """
<b><a href="{package_link}">{package_name}</a></b> by <i>{author_name} {author_email}</i>
平台：<b>{platform}</b>
版本：<b>{version}</b>
许可协议：<b>{license}</b>
摘要：<b>{summary}</b>""".format(
        package_link=f"https://pypi.org/pypi/{args}",
        package_name=pypi_info["name"],
        author_name=pypi_info["author"],
        author_email=f"&lt;{pypi_info['author_email']}&gt;"
        if pypi_info["author_email"]
        else "",
        platform=pypi_info["platform"] or "未指定",
        version=pypi_info["version"],
        license=pypi_info["license"] or "未指定",
        summary=pypi_info["summary"],
    )
    await message.edit(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
