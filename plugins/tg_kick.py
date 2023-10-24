import asyncio
from inspect import Parameter

from loguru import logger
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from core import command
from tools.constants import TG_BOT, TG_PRIVATE
from tools.helpers import delete_this, kick_one, show_cmd_tip

"""
data/command.yml

nosee:
  cmd: nosee
  format: -nosee
  usage: 回复一条消息，将在所有共同且拥有管理踢人权限的群组中踢出目标消息的主人


"""


@Client.on_message(command('nosee'))
async def sb(cli: Client, msg: Message):
    """回复一条消息，将在所有共同且拥有管理踢人权限的群组中踢出目标消息的主人"""
    cmd, *_ = Parameter.get(msg)
    reply_to_message = msg.reply_to_message
    if not reply_to_message or msg.chat.type in [TG_BOT, TG_PRIVATE]:
        return await show_cmd_tip(msg, cmd)

    counter, target = 0, reply_to_message.from_user
    common_groups = await target.get_common_chats()
    logger.info(
        f"开始从各个群聊中踢出此用户 <{target.first_name}{target.last_name} <{target.id}>")
    for chat in common_groups:
        try:
            if await kick_one(cli, chat.id, target.id):
                counter = counter + 1

        except FloodWait as e:
            await asyncio.sleep(e.x)
            if await kick_one(cli, chat.id, target.id):
                counter = counter + 1
                logger.success(
                    f"已将该用户踢出 <{chat.tile} {chat.id}>"
                )

        except RPCError as e:
            logger.warning(
                f"此群聊中没有管理员权限 <{chat.title} {chat.id}>")
            logger.warning(e)

    # delete this user all messages
    await cli.delete_user_history(msg.chat.id, target.id)

    # Inform
    text = f"😂 在 {counter} 个公共群聊中踢出了 {target.mention(style=ParseMode.MARKDOWN)} 。"
    await msg.edit_text(text)
    await asyncio.sleep(10)
    await delete_this(msg)
    # log
    logger.success(f"{cmd} | {text}")
    await logger.complete()
