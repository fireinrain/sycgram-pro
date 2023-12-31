import asyncio
import os

from loguru import logger
from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.constants import DOWNLOAD_PATH, SYCGRAM
from tools.helpers import Parameters, delete_this, show_cmd_tip, show_exception

"""
data/command.yml

transfer:
  cmd: trsf
  format: -trsf <up|down> <文件路径(相对于机器人来说)>|<无|文件路径>
  usage: 上传容器内文件至当前对话(-trsf up xxxxx),回复一条文件/视频/图片/音乐等可下载的消息。如无指定文件路径，则默认存放至data目录(-trsf down 无|指定下载路径)


"""


@Client.on_message(command("transfer"))
async def upload(cli: Client, msg: Message):
    cmd, args = Parameters.get(msg)
    args_list = args.split(" ", maxsplit=1)
    if len(args_list) == 1:
        return await msg.edit_text("请输入正确的参数!")
    if len(args_list) == 2:
        subcmd = args_list[0]

        if subcmd == "up":
            msg = args
            """上传文件"""
            cmd, where = Parameters.get(msg)
            if not where:
                return await show_cmd_tip(msg, cmd)
            replied_msg_id = msg.reply_to_message.id \
                if msg.reply_to_message else None
            _, filename = os.path.split(where)
            try:
                res = await cli.send_document(
                    chat_id=msg.chat.id,
                    document=where,
                    caption=f"```From {SYCGRAM}```",
                    file_name=filename,
                    reply_to_message_id=replied_msg_id
                )
            except Exception as e:
                return await show_exception(msg, e)
            else:
                if res:
                    await delete_this(msg)
                else:
                    await msg.edit_text("⚠️ 可能上传失败 ...")
        elif subcmd == "down":
            msg = args
            """下载目标消息的文件"""
            cmd, where = Parameters.get(msg)
            replied_msg = msg.reply_to_message
            if not replied_msg:
                return await show_cmd_tip(msg, cmd)

            try:
                res = await replied_msg.download(
                    file_name=DOWNLOAD_PATH if not where else where)
            except ValueError:
                return await show_cmd_tip(msg, cmd)
            except Exception as e:
                logger.error(e)
                return await show_exception(msg, e)
            else:
                if res:
                    await msg.edit_text("✅ 下载成功。")
                    await asyncio.sleep(3)
                    await delete_this(msg)
                else:
                    await msg.edit_text("⚠️ 可能下载失败 ...")


"""
data/command.yml

upload:
  cmd: upload
  format: -upload <文件路径>
  usage: 上传容器内文件至当前对话
"""

# @Client.on_message(command("upload"))
# async def upload(cli: Client, msg: Message):
#     """上传文件"""
#     cmd, where = Parameters.get(msg)
#     if not where:
#         return await show_cmd_tip(msg, cmd)
#     replied_msg_id = msg.reply_to_message.id \
#         if msg.reply_to_message else None
#     _, filename = os.path.split(where)
#     try:
#         res = await cli.send_document(
#             chat_id=msg.chat.id,
#             document=where,
#             caption=f"```From {SYCGRAM}```",
#             file_name=filename,
#             reply_to_message_id=replied_msg_id
#         )
#     except Exception as e:
#         return await show_exception(msg, e)
#     else:
#         if res:
#             await delete_this(msg)
#         else:
#             await msg.edit_text("⚠️ 可能上传失败 ...")


"""
data/command.yml

download:
  cmd: download
  format: -download <无|文件路径>
  usage: 回复一条文件/视频/图片/音乐等可下载的消息。如无指定文件路径，则默认存放至data目录

"""
# @Client.on_message(command("download"))
# async def download(_: Client, msg: Message):
#     """下载目标消息的文件"""
#     cmd, where = Parameters.get(msg)
#     replied_msg = msg.reply_to_message
#     if not replied_msg:
#         return await show_cmd_tip(msg, cmd)
#
#     try:
#         res = await replied_msg.download(
#             file_name=DOWNLOAD_PATH if not where else where)
#     except ValueError:
#         return await show_cmd_tip(msg, cmd)
#     except Exception as e:
#         logger.error(e)
#         return await show_exception(msg, e)
#     else:
#         if res:
#             await msg.edit_text("✅ 下载成功。")
#             await asyncio.sleep(3)
#             await delete_this(msg)
#         else:
#             await msg.edit_text("⚠️ 可能下载失败 ...")

# upload:
#   cmd: upload
#   format: -upload <文件路径(相对于机器人Client来说)>
#   usage: 上传容器内文件至当前对话
#
# download:
#   cmd: download
#   format: -download <无|文件路径>
#   usage: 回复一条文件/视频/图片/音乐等可下载的消息。如无指定文件路径，则默认存放至data目录
