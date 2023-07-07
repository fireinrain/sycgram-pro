import asyncio
import re
from random import choice, random
from typing import List

from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from tools.constants import CC_MAX_TIMES, REACTIONS, STORE_CC_DATA, TG_GROUPS
from tools.helpers import Parameters, delete_this, emoji_sender, show_cmd_tip
from tools.storage import SimpleStore


@Client.on_message(command('cc'))
async def cc(cli: Client, msg: Message):
    """
    cc:
    format: -cc <数量> or -cc <emoji|set>
    usage:
        回复使用：遍历该消息的主人发过的消息并丢<数量>个<emoji>给Ta；直接使用：
        指令<emoji>为默认emoji。默认：💩
    """
    cmd, opt = Parameters.get(msg)
    replied_msg = msg.reply_to_message

    async with SimpleStore(auto_flush=False) as store:
        cc_emoji = store.data.get(STORE_CC_DATA)
        if not cc_emoji:
            cc_emoji = store.data[STORE_CC_DATA] = '💩'

        if replied_msg and bool(re.match(r"[0-9]+", opt)):
            cc_times = int(opt)
        elif opt in REACTIONS or opt == 'set':
            store.data[STORE_CC_DATA] = choice(
                REACTIONS) if opt == 'set' else opt
            tmp = store.data[STORE_CC_DATA]
            store.flush()
            await msg.edit_text(f"默认的表情将更改成 `{tmp}`")
            return
        else:
            return await show_cmd_tip(msg, cmd)

    # 攻击次数
    cc_times = cc_times if 1 <= cc_times <= CC_MAX_TIMES else CC_MAX_TIMES
    cc_msgs: List[int] = []
    from_user_id = replied_msg.from_user.id if replied_msg.from_user else replied_msg.sender_chat.id

    # 遍历和搜索消息
    if msg.chat.type in TG_GROUPS:
        async for target in cli.search_messages(
            chat_id=msg.chat.id, limit=1000,
            from_user=from_user_id,
        ):
            if target.id > 1 and (target.from_user or target.sender_chat):
                cc_msgs.append(target.id)
                if len(cc_msgs) == cc_times:
                    break
    else:
        async for target in cli.get_chat_history(msg.chat.id, limit=1000):
            print("traget 类型",type(target))
            if target.id > 1 and target.from_user and \
                    target.from_user.id == replied_msg.from_user.id:
                cc_msgs.append(target.id)
                if len(cc_msgs) == cc_times:
                    break

    if len(cc_msgs) > 0:
        await msg.edit_text("🔥 `攻击中 ...`")
        shot = 0
        for n, cc_msg_id in enumerate(cc_msgs):
            try:
                res = await emoji_sender(
                    cli=cli,
                    chat_id=msg.chat.id,
                    msg_id=cc_msg_id,
                    emoji=cc_emoji
                )
            except FloodWait as e:
                await asyncio.sleep(e + 1)
                res = await emoji_sender(
                    cli=cli,
                    chat_id=msg.chat.id,
                    msg_id=cc_msg_id,
                    emoji=cc_emoji
                )

            if not res and shot == 0:
                await msg.edit_text(
                    f"这个聊天不允许使用 {cc_emoji} 做出反应."
                )
                return

            shot = shot + 1
            logger.success(f"{cmd} | attacking | {n+1}")
            await asyncio.sleep(random() / 5)
        # Finished
        text = f"✅ 完成，命中率是 {shot/cc_times*100}%"

    else:
        # Finished
        text = "❓ 无法找到攻击目标！"

    await delete_this(msg)
    res = await cli.send_message(msg.chat.id, text)
    await asyncio.sleep(3)
    await delete_this(res)
