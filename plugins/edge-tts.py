from loguru import logger
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.helpers import Parameters, delete_this

import os
import json
import asyncio
import edge_tts
CONFIG_PATH = os.path.join(os.getcwd(), "data", "tts_config.json")
default_config = {
    "voice": "zh-CN-XiaoxiaoNeural",
    "rate": "+0%",
    "volume" : "+0%"
}


async def config_check() -> dict:

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f)
        return default_config

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


async def config_set(short_name: str) -> bool:
    config = await asyncio.create_task(config_check())
    config["voice"] = short_name
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)
        return True
    return False


async def get_audio() -> str:
    return os.path.join(os.getcwd(), "data", "tts.mp3")


@Client.on_message(command('tts'))
async def tts(cli: Client, msg: Message):
    """
    智能语言转换
    how to use
    -tts <direct text|list [str]|set [str]>
    """
    cmd, opt = Parameters.get(msg)
    replied_msg = msg.reply_to_message
    print("要转换的消息",replied_msg)
    if opt.startswith("set "):
        model_name = opt.split(" ")[1]
        status = await asyncio.create_task(config_set(model_name))
        if not status:
            await msg.edit_text('❗️ TTS设置错误')
        await msg.edit_text(
            "成功建立{}语音模型".format(model_name))
    elif opt.startswith("list "):
        tag = opt.split(" ")[1]
        voice_model = await edge_tts.list_voices()
        s = "ShortName               |       Gender      |           FriendlyName\r\n"
        for model in voice_model:
            if tag in model["ShortName"] or tag in model["Locale"]:
                s += "{} | {} | {} \r\n".format(model["ShortName"],
                                                    model["Gender"],
                                                    model["FriendlyName"])
        await msg.edit_text(s)
    elif opt is not None and opt != " " and opt != '':
        config = await asyncio.create_task(config_check())
        mp3_buffer = edge_tts.Communicate(text=opt,
                                      voice=config["voice"],
                                      rate=config["rate"],
                                      volume=config['volume'])
        await mp3_buffer.save(audio_fname="./data/tts.mp3")
        mp3_path = "./data/tts.mp3"
        if replied_msg is None:
            await msg.reply_voice(mp3_path)
            await delete_this(msg)
        else:
            await msg.reply_voice(
                mp3_path, reply_to_message_id=replied_msg.id)
            await delete_this(msg)
    elif replied_msg is not None:
        config = await asyncio.create_task(config_check())
        mp3_buffer = edge_tts.Communicate(text=replied_msg.text,
                                      voice=config["voice"],
                                      rate=config["rate"],
                                      volume=config['volume'])
        await mp3_buffer.save(audio_fname="./data/tts.mp3")
        mp3_path = "./data/tts.mp3"
        await msg.reply_voice(mp3_path,
                              reply_to_message_id=replied_msg.id)
        await delete_this(msg)
    elif opt is None or opt == " ":
        await msg.edit_text("错误，请使用帮助命令显示用例")


'''
in commmand.yml
mtts:
  cmd: mtts
  format: -mtts text
  usage: tts AI 语音转换,-mtts list zh 模糊搜索列出含有zh字符的语音模型, -mtts set zh-CN-YunfengNeural 使用zh-CN-YunfengNeural语音模型
'''

