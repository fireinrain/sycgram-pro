import asyncio
from math import floor
from typing import Optional

import emoji
from loguru import logger
from PIL import Image, UnidentifiedImageError
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from .constants import STICKER_BOT, STICKER_IMG
from .helpers import Parameters, delete_this


class StickerLocker:
    """贴纸指令🔒"""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    def get_lock(self) -> None:
        return self._lock


sticker_locker = StickerLocker()


class StickerEvent:
    """贴纸对话事件"""

    def __init__(self) -> None:
        self._cond = asyncio.Condition()

    def get_response(self) -> asyncio.Condition:
        return self._cond

    def wait(self):
        return self._cond.wait()

    def notify(self):
        return self._cond.notify()


sticker_cond = StickerEvent()


class StickerAdder:
    """
    新增贴纸的指令`-s`实现详细步骤：
    1、解禁机器人(`@Stickers`)
    2、发送/cancel
    3、检测目标消息是否为贴纸
        是：
            3-1、转发贴纸到@Stickerss
            3-2、获取并发送emoji
            3-3、发送/done
            3-4、结束指令
    4、若不是，则检测是否为图片或图片格式的文件
        1、转化图片

    """

    def __init__(self, cli: Client, msg: Message) -> None:
        self._cli = cli
        self._msg = msg
        self._bot_id = STICKER_BOT
        self._count = 0

    def is_finished(self, pkg_existed: bool) -> bool:
        return (pkg_existed and self._count == 6) or \
            (not pkg_existed and self._count == 8)

    async def do_cancel(self) -> None:
        """取消原指令残留效果"""
        self._count = 0
        await self.send_message('/cancel')

    async def send_message(self, text: str) -> None:
        """发送指令(或`emoji`)给贴纸"""

        try:
            await self._cli.send_message(
                self._bot_id, text,
                disable_notification=True)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await self._cli.send_message(
                self._bot_id, text,
                disable_notification=True)
        except RPCError as e:
            logger.warning(e)
        else:
            await self.__wait_for()

    async def send_emoji(self) -> None:
        _, arg = Parameters.get(self._msg)
        if emoji.is_emoji(arg):
            an_emoji = arg
        elif self._msg.reply_to_message.sticker:
            an_emoji = self._msg.reply_to_message.sticker.emoji
        else:
            an_emoji = '⚡️'
        await self.send_message(an_emoji)

    async def send_retries(self, n: int) -> None:
        try:
            retry_text = f"⚠️ Retrying {n+1} times ..."
            await self._msg.edit_text(retry_text)
            logger.warning(retry_text)
        except RPCError as e:
            logger.warning(e)
        finally:
            await logger.complete()

    async def upload_photo(self) -> Optional[bool]:
        """下载图片/图片文件，修剪后发送至@Stickers"""
        img = await self._msg.reply_to_message.download(STICKER_IMG)
        if not img:
            return True
        try:
            resize_image(img)
        except UnidentifiedImageError as e:
            logger.warning(e)
            return True

        try:
            await self._cli.send_document(
                self._bot_id, document=img)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await self._cli.send_document(
                self._bot_id, document=img)
        except RPCError as e:
            logger.warning(e)
        else:
            await self.__wait_for()

    async def edit_text(self, text, parse_mode: Optional[str] = None) -> None:
        """编辑消息"""
        try:
            await self._msg.edit_text(text, parse_mode=parse_mode)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await self._msg.edit_text(text, parse_mode=parse_mode)
        except RPCError as e:
            logger.warning(e)

    async def done(self, text: str, parse_mode: Optional[str] = None) -> None:
        try:
            await self.edit_text(text, parse_mode=parse_mode)
            await asyncio.sleep(3.5)
            await delete_this(self._msg)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await self.edit_text(text, parse_mode=parse_mode)
            await asyncio.sleep(3.5)
            await delete_this(self._msg)
        except RPCError as e:
            logger.warning(e)

    async def mark_as_read(self) -> None:
        """自动已读机器人的消息"""
        try:
            await self._cli.get_chat_history(self._bot_id)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await self._cli.get_chat_history(self._bot_id)
        except RPCError as e:
            logger.warning(e)
        except Exception as e:
            logger.error(e)

    async def __wait_for(self) -> None:
        """等待贴纸机器人(`@Stickers`)的回应"""
        async with sticker_cond.get_response():
            await asyncio.wait_for(sticker_cond.wait(), timeout=5)
            logger.debug(
                f"Counter of response from @Stickers is {self._count}"
            )
            self._count = self._count + 1
            await self.mark_as_read()


def resize_image(photo: str):
    with Image.open(photo) as img:
        maxsize = (512, 512)
        if img.width < 512 or img.height < 512:
            w = img.width
            h = img.height
            if w > h:
                scale = 512 / w
                size1new = 512
                size2new = h * scale
            else:
                scale = 512 / h
                size1new = w * scale
                size2new = 512
            size_new = (floor(size1new), floor(size2new))
            img = img.resize(size_new)
        else:
            img.thumbnail(maxsize)
        img.save(photo, format='png')
        return


def isEmoji(content):
    if not content:
        return False
    if u"\U0001F600" <= content <= u"\U0001F64F":
        return True
    elif u"\U0001F300" <= content <= u"\U0001F5FF":
        return True
    elif u"\U0001F680" <= content <= u"\U0001F6FF":
        return True
    elif u"\U0001F1E0" <= content <= u"\U0001F1FF":
        return True
    else:
        return False
