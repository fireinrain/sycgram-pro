import random

from pyrogram import Client
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters

"""
data/command.yml

atadmin:
  cmd: atadm
  format: -atadm <消息内容>
  usage: 一键发送消息@本群管理员(仅在群组中有效)
"""


@Client.on_message(command("atadmin"))
async def at_admins(client: Client, message: Message):
    admins = []
    async for m in client.get_chat_members(
            message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        if not m.user.is_bot and not m.user.is_deleted:
            admins.append(m.user.mention)
    if not admins:
        return await message.edit_text("❌ 本群组没有管理员")
    cmd, args = Parameters.get(message)
    if not args:
        return await message.edit_text("请输入需要发送的消息内容")

    args_list = args.split(" ", maxsplit=1)
    if args_list[0] == "all":
        say = args_list[1] or "召唤本群所有管理员"
        send_list = " , ".join(admins)
        await client.send_message(
            message.chat.id,
            "%s：\n\n%s" % (say, send_list),
            reply_to_message_id=message.reply_to_message_id
                                or message.reply_to_top_message_id,
        )
    if args_list[0] == "random":
        say = args_list[1] or "召唤本群所有管理员"
        send_id = random.choice(admins)
        await client.send_message(
            message.chat.id,
            "%s：\n\n%s" % (say, send_id),
            reply_to_message_id=message.reply_to_message_id
                                or message.reply_to_top_message_id,
        )
    else:
        # 单个管理员
        say = None
        if len(args_list) == 1:
            say = args_list[0] or "召唤本群所有管理员"
        else:
            say = args_list[0] + " " + args_list[1] or "召唤本群所有管理员"
        send_id = admins[0]
        await client.send_message(
            message.chat.id,
            "%s：\n\n%s" % (say, send_id),
            reply_to_message_id=message.reply_to_message_id
                                or message.reply_to_top_message_id,
        )
    await message.delete()
