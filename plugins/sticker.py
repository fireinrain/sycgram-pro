import asyncio
from time import time

from core import command
from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message
from tools.constants import STICKER_BOT, STICKER_ERROR_LIST
from tools.helpers import (Parameters, check_if_package_existed,
                           get_default_pkg, show_exception)
from tools.stickers import StickerAdder, sticker_cond, sticker_locker
from tools.storage import SimpleStore
from pyrogram.enums import ParseMode 

@Client.on_message(filters.incoming & filters.user(STICKER_BOT), group=-1)
async def sticker_event(cli: Client, msg: Message):
    async with sticker_cond.get_response():
        if msg.text not in STICKER_ERROR_LIST:
            sticker_cond.notify()
            logger.success(f"Receive @Stickers response | {msg.text}")
        else:
            async with SimpleStore() as store:
                me = await cli.get_me()
                pkg_title, pkg_name = get_default_pkg(me)
                store.data['sticker_error'] = msg.text
                store.data['sticker_set_title'] = pkg_title
                store.data['sticker_set_name'] = pkg_name
                logger.error(f"Receive @Stickers error | {msg.text}")
    await logger.complete()


@Client.on_message(command('sticker'))
async def sticker(cli: Client, msg: Message):
    """
    用法一：-s <emoji|无> 回复一条消息
    用法二：-s <sticker_set_title> <sticker_set_name> 切换默认贴纸包标题和名字
    作用：偷为静态贴纸（对象：贴纸/图片/图片文件）
    """
    _, args = Parameters.get_more(msg)
    if not msg.reply_to_message:
        # 处理参数
        if len(args) != 2:
            pkg_title, pkg_name = get_default_pkg(msg.from_user)
            await msg.edit_text('✅ 正在将贴纸标题和名称重置为默认值..')
        else:
            pkg_title, pkg_name = args
            if len(pkg_title.encode()) >= 168:
                await msg.edit_text('❗️ 贴纸标题太长。')
                return
            elif len(pkg_name.encode()) >= 58:
                await msg.edit_text('❗️ 贴纸名称太长。')
                return
            await msg.edit_text('✅ 自定义贴纸标题和名称成功。')

        async with SimpleStore() as store:
            store.data['sticker_set_title'] = pkg_title
            store.data['sticker_set_name'] = pkg_name
        return

    async with SimpleStore(auto_flush=False) as store:
        pkg_title = store.data.get('sticker_set_title')
        pkg_name = store.data.get('sticker_set_name')
        if not pkg_title or not pkg_name:
            return await msg.edit_text(
                "⚠️ 默认标签标题和名称为空, "
                "请使用 `-s reset`!"
            )

    # 尝试检查贴纸包是否存在
    try:
        pkg_existed = await check_if_package_existed(pkg_name)
    except Exception as e:
        # 无法判定是否贴纸包存在
        logger.error(e)
        return await show_exception(msg, e)

    # 开始前的检查
    await msg.edit_text('👆 正在努力添加贴纸 ...')
    status = await cli.unblock_user(STICKER_BOT)
    # 开始偷贴纸
    async with sticker_locker.get_lock():
        try:
            await sticker_helper(
                cli=cli,
                msg=msg,
                pkg_title=pkg_title,
                pkg_name=pkg_name,
                pkg_existed=pkg_existed,
            )
        except asyncio.exceptions.TimeoutError:
            async with SimpleStore() as store:
                sticker_error = store.data.get('sticker_error')
                store.data.pop('sticker_error', None)
                await msg.edit_text(f"❌ 错误\n```{sticker_error}```")
        except TypeError:
            await msg.edit_text("😭 不是静态图像，现在停止添加 ...")
        except Exception as e:
            logger.error(e)
            await msg.edit_text("😭 添加贴纸失败，现已停止添加 ...")
        finally:
            await logger.complete()


async def sticker_helper(
    cli: Client,
    msg: Message,
    pkg_title: str,
    pkg_name: str,
    pkg_existed: bool,
):
    replied = msg.reply_to_message
    if not (replied.sticker or replied.photo or (
        replied.document and
        'image' in replied.document.mime_type
    )):
        raise TypeError("这不是图片")

    start, adder = time(), StickerAdder(cli, msg)
    # ---------------- 目标消息为：贴纸 ----------------
    success = f"👍 完成于： <time> 并点击 [这里](https://t.me/addstickers/{pkg_name}) 查看."
    # Up to 3 attempts
    for attempts in range(3):
        if pkg_existed:
            # counter == 6
            await adder.do_cancel()
            await adder.send_message('/addsticker')
            await adder.send_message(pkg_name)
            if await adder.upload_photo():
                continue
            await adder.send_emoji()
            await adder.send_message('/done')

        else:
            # counter == 8
            await adder.do_cancel()
            await adder.send_message('/newpack')
            await adder.send_message(pkg_title)
            if await adder.upload_photo():
                continue
            await adder.send_emoji()
            await adder.send_message('/publish')
            await adder.send_message('/skip')
            await adder.send_message(pkg_name)

        if adder.is_finished(pkg_existed):
            success = success.replace('<time>', f'{time()-start:.3f}', 1)
            await adder.done(success, parse_mode=ParseMode.MARKDOWN)
            return
        else:
            adder.send_retries(attempts)

    failure = "😭 添加贴纸失败，现已停止添加 ..."
    await adder.done(failure, 'md')
    logger.warning(failure)
    await logger.complete()
    return
