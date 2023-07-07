import re
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.helpers import Parameters
from tools.sessions import session
from loguru import logger


@Client.on_message(command('bin'))
async def card(client: Client, msg: Message):
    """_summary_
    卡组织查询
    Args:
        _ (Client): _description_
        msg (Message): _description_
    """
    cmd, arg = Parameters.get(msg)
    me=await client.get_me()
    # print(me,dir(me),me.id,me.username)
    try:
        resp=await session.get("https://api.freebinchecker.com/bin/{}".format(arg),timeout=5.5)
        
        # if resp.status == 404:
        #     await msg.edit_text("卡头不存在")
        #     return 
        # elif resp.status==429:
        #     await msg.edit_text("请求速度过快,请稍后再试")
        #     return 
        # elif  resp.status !=200:
        #     await msg.edit_text("发生其他错误")
        #     return 
        bin_json=await resp.json()
        if bin_json['valid'] == "false":
            await msg.edit_text("卡头不存在")
            return 
        if "name" in bin_json['issuer']:
            bank_name=bin_json['issuer']["name"]
        else:
            bank_name="未知"
        txt=f"[*]卡BIN: {arg}\n[*]卡品牌: {bin_json['card']['scheme']}\n[*]卡类型: {bin_json['card']['type']}\n[*]发卡行: {bank_name}\n[*]发卡国家: {bin_json['country']['name']}\n"
        if bin_json["card"]["prepaid"]=="true":
            txt+="[*]是否为预付卡:是\n"
        else:
            txt+="[*]是否为预付卡:否\n"   
        await msg.edit_text(txt)
    except Exception as e:
        await msg.edit_text(e)
        return
    
    

"""
data/command.yml
bin:
  cmd: bin
  format: -bin cardnumber
  usage: 发卡行查询
"""