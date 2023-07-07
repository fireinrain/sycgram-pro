from loguru import logger
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.helpers import Parameters, delete_this
from pymtts import async_Mtts
import os
import json

CONFIG_PATH = os.path.join(os.getcwd(), "data", "mtts_config.json")
default_config = {
    "short_name": "zh-CN-XiaoxiaoNeural",
    'style': "general",
    "rate": 0,
    "pitch": 0,
    "kmhz": 24
}


async def config_check() -> dict:

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f)
        return default_config

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


async def config_set(short_name: str) -> bool:
    config = await config_check()
    config["short_name"] = short_name
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)
        return True
    return False


async def save_audio(buffer: bytes) -> str:
    with open(os.path.join(os.getcwd(), "data", "mtts.mp3"), "wb") as f:
        f.write(buffer)
        return os.path.join(os.getcwd(), "data", "mtts.mp3")


@Client.on_message(command('mtts'))
async def mtts(cli: Client, msg: Message):
    """
    智能语言转换
    how to use
    -mtts <direct text|list [str]|set [str]>
    """
    cmd, opt = Parameters.get(msg)
    replied_msg = msg.reply_to_message
    print("要恢复的信息",replied_msg)
    cmtts = async_Mtts()
    if opt.startswith("set "):
        model_name = opt.split(" ")[1]
        status = await config_set(model_name)
        if not status:
            await msg.edit_text('❗️ TTS设置错误')
        await msg.edit_text(
            "成功建立{}语音模型".format(model_name))
    elif opt.startswith("list "):
        tag = opt.split(" ")[1]
        voice_model = await cmtts.get_lang_models()
        s = "code | local name | Gender | LocaleName\r\n"
        for model in voice_model:
            if tag in model.ShortName or tag in model.Locale or tag in model.LocaleName:
                s += "{} | {} | {} | {}\r\n".format(model.ShortName,
                                                    model.LocalName,
                                                    model.Gender,
                                                    model.LocaleName)
        await msg.edit_text(s)
    elif opt is not None and opt != " " and opt != '':
        config = await config_check()
        mp3_buffer = await cmtts.mtts(text=opt,
                                      short_name=config["short_name"],
                                      style=config["style"],
                                      rate=config["rate"],
                                      pitch=config['pitch'],
                                      kmhz=config["kmhz"])
        mp3_path = await save_audio(mp3_buffer)

        if replied_msg is None:
            await msg.reply_voice(mp3_path)
            await delete_this(msg)
        else:
            await msg.reply_voice(
                mp3_path, reply_to_message_id=replied_msg.id)
            await delete_this(msg)
    elif replied_msg is not None:
        config = await config_check()
        mp3_buffer = await cmtts.mtts(text=replied_msg.text,
                                      short_name=config["short_name"],
                                      style=config["style"],
                                      rate=config["rate"],
                                      pitch=config['pitch'],
                                      kmhz=config["kmhz"])
        mp3_path = await save_audio(mp3_buffer)
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

