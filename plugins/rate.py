from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.types import Message
from tools.constants import RATE_API
from tools.helpers import Parameters
from tools.sessions import session


@Client.on_message(command('ex'))
async def rate(_: Client, msg: Message):
    """查询当天货币汇率，格式：-ex <float> <FROM> <TO>"""
    cmd, args = Parameters.get_more(msg)
    if len(args) != 3:
        failure = f"❗️ 请这样使用 `{cmd} 1 usd cny`，它将从美元兑换成人民币。"
        await msg.edit_text(failure)
        return

    try:
        num = abs(float(args[0]))
    except ValueError:
        await msg.edit_text("❗️ 你应该输入一个数字，你个傻钩子。")
        return
    else:
        __from = args[1].lower()
        __to = args[2].lower()

    for _ in range(10):
        async with session.get(
            f'{RATE_API}/{__from}/{__to}.json', timeout=5.5
        ) as resp:
            try:
                if resp.status == 200:
                    data = await resp.json()
                    result = float(data.get(__to)) * num
                    success = f"```{__from.upper()} : {__to.upper()} = {num} : {result:.5f}```"
                    await msg.edit_text(success)
                    logger.success(success)
                    return
                else:
                    resp.raise_for_status()
            except Exception as e:
                logger.error(e)
                continue
            finally:
                await logger.complete()

    failure = "❗️ 网络错误或货币符号错误，请再试一次。"
    await msg.edit_text(failure)
    return
