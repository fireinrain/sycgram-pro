import asyncio
import re
from typing import Any, Dict, List, Tuple, Union
import os 
from bs4 import BeautifulSoup
from core.custom import CMDS_PREFIX
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message, User

from .constants import STICKER_DESCRIP, SYCGRAM_ERROR, SYCGRAM_INFO
from .sessions import session
from pyrogram.enums import ParseMode 
from configparser import ConfigParser
class Parameters:
    @classmethod
    def get(cls, msg: Message) -> Tuple[str]:
        """返回所需的指令的单个参数，类型为`str`"""
        text = msg.text.split(' ', 1)
        if len(text) > 1:
            return text[0], ''.join(text[1:]).strip()
        else:
            return text[0], ''

    @classmethod
    def get_int(cls, msg: Message, max_num: int = 30) -> Tuple[str, int]:
        """返回所需的指令的单个参数，类型为`int`"""
        cmd, arg = cls.get(msg)
        if not arg or not bool(re.match(r"[0-9]+$", arg)):
            return cmd, 1
        num = int(arg) if 1 <= int(arg) <= max_num else 1
        return cmd, num

    @classmethod
    def get_more(cls, msg: Message) -> Tuple[str, List[str]]:
        cmd, text = cls.get(msg)
        return cmd, [x.strip() for x in text.split(' ') if x]


def get_iterlimit(num: int) -> int:
    """
    Args:
        num (int): 实际删除消息数

    Returns:
        int: 迭代历史消息限制数
    """

    return num * 3 if num * 3 < 1500 else 1500


def get_dc_text(name: str, dc_id: int) -> str:
    text = f"{name} 的数据中心为：`DC{dc_id}`\n该数据中心位于："

    if dc_id == 1 or dc_id == 3:
        return f"{text}`美国佛罗里达州迈阿密`"

    elif dc_id == 2 or dc_id == 4:
        return f"{text}`荷兰北荷兰省阿姆斯特丹`"

    elif dc_id == 5:
        return f"{text}`新加坡`"

    else:
        return "❗️ 无法获取该用户/群组的数据中心 ..."


def get_sender_name(msg: Message) -> str:
    if msg.from_user:
        return get_fullname(msg.from_user)
    return msg.sender_chat.title


def get_fullname(user: User) -> str:
    if user:
        if user.last_name:
            return f"{user.first_name} {user.last_name}"
        return user.first_name

    else:
        return "匿名"


def get_default_pkg(user: User) -> Tuple[str]:
    if user.username:
        return f"@{user.username} 的贴纸包(1)", f"{user.username}_1"

    return f"@{user.first_name} 的贴纸包(1)", f"tmp_{user.id}_1"


def is_deleted_id(msg: Message) -> bool:
    return bool(msg.id > 1 and msg.from_user and msg.from_user.is_self)


async def show_exception(msg: Message, e: Any) -> None:
    text = f"**{SYCGRAM_ERROR}**\n> # `{e}`"
    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)


async def show_cmd_tip(msg: Message, cmd: str) -> str:
    tip = f"使用 `{CMDS_PREFIX}help {cmd.replace(CMDS_PREFIX, '', 1)}` 查看详细使用示例。"
    text = f"**{SYCGRAM_INFO}**\n> # {tip}"
    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)


async def check_if_package_existed(pkg_name: str) -> bool:
    """检测贴纸包是否存在

    Args:
        pkg_name (`str`): 贴纸包名字

    Raises:
        ValueError: 无法检测贴纸包是否存在

    Returns:
        bool: `True`为贴纸包存在，`False`为贴纸包不存在
    """
    async with session.get(
        f'https://t.me/addstickers/{pkg_name}', timeout=9.9,
    ) as resp:
        if resp.status == 200:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            target = soup.find(
                'div', class_='tgme_page_description').text.strip()
            return not bool(STICKER_DESCRIP == target)
        else:
            resp.raise_for_status()

    raise ValueError("无法检查贴纸包是否存在。")


async def emoji_sender(
    cli: Client,
    chat_id: Union[int, str],
    msg_id: int,
    emoji: str = '',
) -> bool:
    try:
        await cli.send_reaction(chat_id, msg_id, emoji)
    except FloodWait as e:
        raise e
    except RPCError:
        return False
    else:
        return True


async def delete_this(msg: Message) -> None:
    try:
        await msg.delete()
    except RPCError as e:
        logger.warning(e)
        await logger.complete()


async def basher(cmd: str, timeout: int = 10) -> Dict[str, Any]:
    return await asyncio.wait_for(execute(cmd), timeout=timeout)


async def execute(command: str) -> Dict[str, Any]:
    executor = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await executor.communicate()
    except Exception as e:
        return {'output': '', 'error': str(e)}
    else:
        return {
            'output': stdout.decode('utf-8', 'ignore').strip(),
            'error': stderr.decode('utf-8', 'ignore').strip()
        }


async def kick_one(cli: Client, cid: Union[int, str], uid: Union[int, str]):
    me = await cli.get_chat_member(cid, 'me')
    if me.can_restrict_members and await cli.ban_chat_member(cid, uid):
        return True

    return False


def escape_markdown(text: str, version: int = 1, entity_type: str = None) -> str:
    """
    Helper function to escape telegram markup symbols.
    Args:
        text (:obj:`str`): The text.
        version (:obj:`int` | :obj:`str`): Use to specify the version of telegrams Markdown.
            Either ``1`` or ``2``. Defaults to ``1``.
        entity_type (:obj:`str`, optional): For the entity types ``PRE``, ``CODE`` and the link
            part of ``TEXT_LINKS``, only certain characters need to be escaped in ``MarkdownV2``.
            See the official API documentation for details. Only valid in combination with
            ``version=2``, will be ignored else.
    """
    if int(version) == 1:
        escape_chars = r'_*`['
    elif int(version) == 2:
        if entity_type in ['pre', 'code']:
            escape_chars = r'\`'
        elif entity_type == 'text_link':
            escape_chars = r'\)'
        else:
            escape_chars = r'_*[]()~`>#+-=|{}.!'
    else:
        raise ValueError('Markdown版本必须是1或2!')

    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


class BotConfigParser:
    def __init__(self, config_path: str = os.path.join(os.getcwd(), "data/config.ini")):
        self._config_path = config_path
        self.config = ConfigParser()


    def config_read(self):
        try:
            self.config.read(self._config_path, encoding="utf-8")
        except Exception as e:
            logger.error(e)
            return None

    def get_config(self):
        self.config_read()
        return self.config