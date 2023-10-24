import contextlib

from typing import List, Optional

from datetime import datetime

from pyrogram.enums import ChatType
from pyrogram.raw.functions.account import GetAuthorizations, ResetAuthorization
from pyrogram.raw.types import Authorization
from pyrogram.types import Message
from pyrogram import Client
from core import command
from tools.helpers import Parameters


async def get_all_session(client: Client) -> List[Authorization]:
    data = await client.invoke(GetAuthorizations())
    return data.authorizations


async def filter_session(client: Client, hash_start: str) -> Optional[Authorization]:
    try:
        hash_start = int(hash_start)
        if len(str(hash_start)) != 6 and hash_start != 0:
            return None
    except ValueError:
        return None
    return next(
        (
            session
            for session in await get_all_session(client)
            if str(session.hash).startswith(str(hash_start))
        ), None,
    )


async def kick_session(session: Authorization, client: Client) -> bool:
    if session.hash != 0:
        with contextlib.suppress(Exception):
            return await client.invoke(ResetAuthorization(hash=session.hash))
    return False


def format_timestamp(timestamp: int) -> str:
    datetime_obj = datetime.fromtimestamp(timestamp)
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")


def format_session(session: Authorization, private: bool = True) -> str:
    text = (
        f"标识符：<code>{str(session.hash)[:6]}</code>\n"
        f"设备型号：<code>{session.device_model}</code>\n"
        f"设备平台：<code>{session.platform}</code>\n"
        f"系统版本：<code>{session.system_version}</code>\n"
        f"应用名称：<code>{session.app_name}</code>\n"
        f"应用版本：<code>{session.app_version}</code>\n"
        f"官方应用：<code>{'是' if session.official_app else '否'}</code>\n"
        f"登录时间：<code>{format_timestamp(session.date_created)}</code>\n"
        f"在线时间：<code>{format_timestamp(session.date_active)}</code>"
    )
    if private:
        text += (
            f"\nIP：<code>{session.ip}</code>\n" f"地理位置：<code>{session.country}</code>"
        )
    if session.hash != 0:
        text += f"\n\n使用命令 <code>,tgsession logout {str(session.hash)[:6]}</code> 可以注销此会话。"
    return text


async def count_platform(client: Client, private: bool = True) -> str:
    sessions = await get_all_session(client)
    if not sessions:
        return "无任何在线设备？"
    platform_count = {}
    text = f"共有 {len(sessions)} 台设备在线，分别是：\n\n"
    for session in sessions:
        if session.platform in platform_count:
            platform_count[session.platform] += 1
        else:
            platform_count[session.platform] = 1
        text += f"<code>{str(session.hash)[:6]}</code> - <code>{session.device_model}</code>"
        if private:
            text += f" - <code>{session.app_name}</code>"
        text += f"\n"
    text += "\n"
    text += "\n".join(
        f"{platform}：{count} 台" for platform, count in platform_count.items()
    )
    return text


"""
data/command.yml


tgsession:
  cmd: tgsess
  format: -tgsess <query|logout> <标识符>
  usage: 查询/注销已登录的Telegram会话
  
"""


@Client.on_message(command("tgsession"))
async def session_manage(client: Client, message: Message):
    cmd, args = Parameters.get(message)

    if not args:
        return await message.edit_text(
            await count_platform(
                client,
                private=message.chat.type in [ChatType.PRIVATE, ChatType.BOT]
            )
        )
    args_list = args.split(" ", maxsplit=1)
    if len(args_list) != 2:
        return await message.edit_text("请输入 `query/logout 标识符` 来查询或注销会话")
    if args_list[0] == "query":
        session = await filter_session(client, message.parameter[1])
        if session:
            return await message.edit_text(
                format_session(
                    session,
                    private=message.chat.type in [ChatType.PRIVATE, ChatType.BOT],
                )
            )
        return await message.edit_text("请输入正确的标识符！")
    if args_list[0] == "logout":
        session = await filter_session(client, message.parameter[1])
        if session:
            success = await kick_session(session, client)
            return await message.edit_text("注销成功！" if success else "注销失败！")
        return await message.edit_text("请输入正确的标识符！")
    return await message.edit_text("请输入 `query/logout 标识符` 来查询或注销会话")
