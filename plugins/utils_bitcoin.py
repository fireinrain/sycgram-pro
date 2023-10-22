from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.helpers import Parameters
from tools.sessions import session
from loguru import logger

EXCHANGE_API = "https://api.exchangerate-api.com/v4/latest/{}"
BIANCE_API = "https://api.binance.com/api/v3/ticker/price?symbol={}USDT"


async def get_from_exchanger(code):
    resp = await session.get(EXCHANGE_API.format(code), timeout=5.5)
    if resp.status == 200:
        data = await resp.json()
        return data["rates"]
    return None


async def get_from_biance(coin):
    resp = await session.get(BIANCE_API.format(coin), timeout=5.5)
    if resp.status == 200:
        data = await resp.json()
        # print("币安",data)
        return float(data["price"])
    return None


"""
data/command.yml
bc:
  cmd: bc
  format: -bc num from to
  usage: 加密货币转换
"""


@Client.on_message(command('bc'))
async def coin(_: Client, msg: Message):
    """_summary_
    加密货币转换器
    Args:
        _ (Client): _description_
        msg (Message): _description_
    """
    cmd, args = Parameters.get_more(msg)
    num = 0.0
    if len(args) != 3:
        fail_msg = f" 这个命令应该这样使用`{cmd} 1 xmr usdt`它将以实时汇率，将1 xmr转换为usdt。"
        await msg.edit_text(fail_msg)
        return
    try:
        num = abs(float(args[0]))
        # print("this is num",num)
    except ValueError:
        await msg.edit_text("你应该输入一个数字，你个傻钩子。")
        return

    _from = args[1].upper()
    _to = args[2].upper()
    try:
        rates = await get_from_exchanger("USD")
        CNY = rates["CNY"]
        if _from in rates:

            from_rates = await get_from_exchanger(_from)
            cny = num * from_rates["CNY"]
            if _to in rates:
                result = num * from_rates[_to]
            else:
                if _to == "USDT":
                    result = num * from_rates[_to]
                else:
                    to_usdt = await get_from_biance(_to)
                    result = num * from_rates["USD"] / to_usdt
        else:
            from_usdt = await get_from_biance(_from)
            cny = num * from_usdt * CNY
            if _to in rates:
                result = num * rates[_to] * from_usdt
            else:
                if _to == "USDT":
                    result = num * from_usdt
                else:
                    to_usdt = await get_from_biance(_to)
                    result = num * from_usdt / to_usdt
        currency = f"{num} {_from} = {result:.8f} {_to} = {cny} CNY \n实时汇率来自于binance"
        await msg.edit_text(currency)
    except Exception as e:
        logger.error(e)
        await msg.edit_text(e)
