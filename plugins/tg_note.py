import asyncio

from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import BadRequest, FloodWait
from pyrogram.types import Message
from tools.constants import STORE_NOTES_DATA
from tools.helpers import Parameters, show_cmd_tip
from tools.storage import SimpleStore

"""
data/command.yml

note:
  cmd: note
  format: -note <save|del> <序号> or -note <序号|list|clear>
  usage: 回复一条消息，根据序号保存/删除该消息文本
"""


@Client.on_message(command('note'))
async def note(_: Client, msg: Message):
    """
    用法一：-note <save|del> <序号>
    用法二：-note <序号|list|clear>
    作用：发送已保存的笔记
    """
    cmd, opts = Parameters.get_more(msg)
    if not (1 <= len(opts) <= 2):
        return await show_cmd_tip(msg, cmd)

    replied_msg = msg.reply_to_message
    async with SimpleStore() as store:
        notes_data = store.get_data(STORE_NOTES_DATA)
        if len(opts) == 2 and opts[0] == 'save' and replied_msg:
            if replied_msg:
                notes_data[opts[1]] = replied_msg.text or replied_msg.caption
                text = "😊 笔记保存成功。"
            else:
                return await show_cmd_tip(msg, cmd)
        elif len(opts) == 2 and opts[0] == 'del':
            if notes_data.pop(opts[1], None):
                text = "😊 笔记删除成功。"
            else:
                text = "❓ 找不到需要删除的笔记。"
        elif len(opts) == 1:
            option = opts[0]
            if option == 'list':
                tmp = '\n'.join(
                    f'`{k} | {v[0:30]} ...`' for k, v in notes_data.items())
                text = f"已保存的笔记：\n{tmp}"
            elif option == 'clear':
                notes_data.clear()
                text = "✅ 所有保存的笔记已被删除。"
            else:
                res = notes_data.get(option)
                text = res if res else f"😱 没有找到{option}对应的笔记 "
        else:
            return await show_cmd_tip(msg, cmd)

    try:
        await msg.edit_text(text)
    except BadRequest as e:
        logger.error(e)  # 存在消息过长的问题，应拆分发送。（就不拆 😊）
    except FloodWait as e:
        logger.warning(e)
        await asyncio.sleep(e.x)
        await msg.edit_text(text)
    finally:
        await logger.complete()
