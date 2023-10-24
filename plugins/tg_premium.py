from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters


@Client.on_message(command("premium"))
async def premium(client: Client, message: Message):
    message = await message.edit_text("正在统计中,请耐心等待...")
    premium_users = users = admins = premium_admins = bots = deleted = 0
    dc_ids = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "failed": 0}
    count = await client.get_chat_members_count(message.chat.id)
    cmd, args = Parameters.get(message)
    if count >= 10000 and args != "force":
        return await message.edit_text(
            "太...太多人了... 我会...会...会坏掉的...\n\n如果您执意要运行的的话，您可以使用指令 ,premium force"
        )
    async for m in client.get_chat_members(message.chat.id):
        if not m.user.is_bot and not m.user.is_deleted:
            users += 1
            try:
                dc_ids[str(m.user.dc_id)] += 1
            except Exception as e:
                dc_ids["failed"] += 1
            if m.user.is_premium:
                premium_users += 1
                if m.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    premium_admins += 1
            if m.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                admins += 1
        elif m.user.is_bot:
            bots += 1
        else:
            deleted += 1
    await message.edit_text(
        f"""**分遗产咯**

管理员:
> 大会员: **{premium_admins}** / 总管理数: **{admins}** 分遗产占比: **{round((premium_admins / admins) * 100, 2) if admins != 0 else '你群管理员全死号?'}%**

用户:
> 大会员: **{premium_users}** / 总用户数: **{users}** 分遗产占比: **{round((premium_users / users) * 100, 2)}%**

> 已自动过滤掉 **{bots}** 个 Bot, **{deleted}** 个 死号

{'***请注意: 由于tg限制 我们只能遍历前10k人 此次获得到的数据并不完整***' if count >= 10000 else ''}""",
        parse_mode=ParseMode.MARKDOWN,
    )
