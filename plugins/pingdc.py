from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.helpers import execute
from pyrogram.enums import ParseMode 

@Client.on_message(command('pingdc'))
async def pingdc(_: Client, msg: Message):
    """到各个DC区的延时"""
    DCs = {
        1: "149.154.175.50",
        2: "149.154.167.51",
        3: "149.154.175.100",
        4: "149.154.167.91",
        5: "91.108.56.130"
    }
    data = []
    for dc in range(1, 6):
        result = await execute(f"ping -c 1 {DCs[dc]} | awk -F '/' " + "'END {print $5}'")
        output = result.get('output')
        data.append(output.replace('\n', '') if output else '-1')

    await msg.edit_text(
        f"🇺🇸 DC1(迈阿密): `{data[0]}`\n"
        f"🇳🇱 DC2(阿姆斯特丹): `{data[1]}`\n"
        f"🇺🇸 DC3(迈阿密): `{data[2]}`\n"
        f"🇳🇱 DC4(阿姆斯特丹): `{data[3]}`\n"
        f"🇸🇬 DC5(新加坡): `{data[4]}`", ParseMode.MARKDOWN
    )
