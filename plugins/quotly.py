import requests
import base64
import asyncio
from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import RPCError
from pyrogram.types import Message
from tools.helpers import Parameters, delete_this
from tools.constants import QUOTLY_API

async def check_replied_msg(msg: Message, cmd: str) -> bool:
    replied_msg = msg.reply_to_message
    if not replied_msg:
        await msg.edit_text(f"❗️ 请使用 `{cmd}` 回复一条消息。")
        await asyncio.sleep(3)
        await delete_this(msg)
        return False
    else:
        return True

async def forward_info(reply):
    # 判断转发来源
    # 转发自频道
    if reply.forward_from_chat:
        sid = reply.forward_from_chat.id
        title = reply.forward_from_chat.title
        name = title
    # 转发自用户或机器人
    elif reply.forward_from:
        sid = reply.forward_from.id
        try:
            try:
                name = first_name = reply.forward_from.first_name
            except TypeError:
                name = '死号'
            if reply.forward_from.last_name:
                last_name = reply.forward_from.last_name
                name = f'{first_name} {last_name}'
        except AttributeError:
            pass
        title = name
    # 拒绝查看转发消息来源时
    elif reply.forward_sender_name:
        title = name = sender_name = reply.forward_sender_name
        sid = 0
    # 不是转发的消息
    elif reply.from_user:
        try:
            sid = reply.from_user.id
            try:
                name = first_name = reply.from_user.first_name
            except TypeError:
                name = '死号'
            if reply.from_user.last_name:
                last_name = reply.from_user.last_name
                name = f'{first_name} {last_name}'
        except AttributeError:
            pass
        title = name
    return sid,title,name

@Client.on_message(command('q'))
async def quote(_: Client, msg: Message):
    json_data = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": "#1b1429",
        "width": 768,
        "height": 768,
        "scale": 2,
        "messages": []
    }
    cmd, opt = Parameters.get_more(msg)
    # 检测是否回复一条消息
    if not await check_replied_msg(msg, cmd):
        return
    # 无参数则默认为当前回复的消息
    if not opt:
        reply = msg.reply_to_message
        sid, title ,name = await forward_info(reply)
        messages_json = {
            "entities": [],
            "avatar": True,
            "from": {
                "id": sid,
                "language_code": "zh",
                "title": title,
                "name": name
            },
            "text": reply.text
        }
        # Add the new message to the 'messages' array
        json_data["messages"].append(messages_json)

        # Convert the updated data back to JSON
        # updated_json = json.dumps(json_data, indent=4)

        await msg.edit('等待Lyosu语录生成返回结果...')
        req = requests.post(QUOTLY_API, json=json_data).json()
        if req['ok'] == True:
            try:
                buffer = base64.b64decode(req['result']['image'].encode('utf-8'))
                open('Quotly.png', 'wb').write(buffer)
                await msg.edit("已在Lyosu生成并保存语录, 正在上传中...")
                await msg.reply_document('Quotly.png',reply_to_message_id=reply.id)
                await delete_this(msg)
            except:
                await msg.edit("请求成功但出现错误❗️ ")
                await asyncio.sleep(3)
                await delete_this(msg)
                return 
            return
    elif int(opt) == 1:
        try:
            num = int(opt[0]) - 1
        except ValueError:
            await msg.edit("❗️ 你应该输入一个数字，你个傻钩子。")
            await asyncio.sleep(3)
            await delete_this(msg)
            return 
        reply = msg.reply_to_message

        sid, title ,name = await forward_info(reply)
        messages_json = {
            "entities": [],
            "avatar": True,
            "from": {
                "id": sid,
                "language_code": "zh",
                "title": title,
                "name": name
            },
            "text": reply.text
        }
        # Add the new message to the 'messages' array
        json_data["messages"].append(messages_json)

        messages = Client.get_chat_history(
            reply.chat.id, 
            limit=num,
            offset_id=reply.id)
        # Extract the message texts
        async for msg in messages:
            sid, title ,name = await forward_info(msg)
            messages_json = {
                "entities": [],
                "avatar": True,
                "from": {
                    "id": sid,
                    "language_code": "zh",
                    "title": title,
                    "name": name
                },
                "text": msg.text
            }
            json_data["messages"].append(messages_json)
        json_data["messages"].reverse()
        await msg.edit('等待Lyosu语录生成返回结果...')
        req = requests.post(QUOTLY_API, json=json_data).json()
        if req['ok'] == True:
            try:
                buffer = base64.b64decode(req['result']['image'].encode('utf-8'))
                open('Quotly.png', 'wb').write(buffer)
                await msg.edit("已在Lyosu生成并保存语录, 正在上传中...")
                await msg.reply_document('Quotly.png',reply_to_message_id=reply.id)
                await delete_this(msg)
            except:
                await msg.edit("请求成功但出现错误")
                await asyncio.sleep(3)
                await delete_this(msg)
                return 
            return
    else:
        await msg.edit("错误，请使用帮助命令显示用例")
        await asyncio.sleep(3)
        await delete_this(msg)
        return 


@Client.on_message(command('faq'))
async def fake_quote(_: Client, msg: Message):
    json_data = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "width": 768,
        "height": 768,
        "scale": 2.5,
        "messages": []
    }
    cmd, opt = Parameters.get_more(msg)
    # 检测是否回复一条消息
    if not await check_replied_msg(msg, cmd):
        return
    # 无参数则默认为当前回复的消息
    if not opt:
        await msg.edit("未指定内容, 无法生成")
        await asyncio.sleep(3)
        await delete_this(msg)
        return 
    else:
        reply = msg.reply_to_message

        sid, title ,name = await forward_info(reply)
        messages_json = {
            "entities": [],
            "avatar": True,
            "from": {
                "id": sid,
                "language_code": "zh",
                "title": title,
                "name": name
            },
            "text": opt
        }
        # Add the new message to the 'messages' array
        json_data["messages"].append(messages_json)

        # Convert the updated data back to JSON
        # updated_json = json.dumps(json_data, indent=4)

        await msg.edit('等待Lyosu语录生成返回结果...')
        req = requests.post(QUOTLY_API, json=json_data).json()
        if req['ok'] == True:
            try:
                buffer = base64.b64decode(req['result']['image'].encode('utf-8'))
                open('Quotly.png', 'wb').write(buffer)
                await msg.edit("已在Lyosu生成并保存语录, 正在上传中...")
                await msg.reply_document('Quotly.png',reply_to_message_id=reply.id)
                await delete_this(msg)
            except:
                await msg.edit("请求成功但出现错误")
                await asyncio.sleep(3)
                await delete_this(msg)
                return 
            return
