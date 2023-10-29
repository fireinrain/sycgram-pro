import time

from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters
from pyrogram.enums import ParseMode

from core.custom import CMDS_DATA
import openai

fakeopen_base = 'https://ai.fakeopen.com/v1/'


def get_access_token() -> str:
    return CMDS_DATA.get('chatgpt')['access_token']


def fakeopen_api(query: str, max: int, stream_true: bool, tem: float):
    openai.api_base = fakeopen_base
    openai.api_key = get_access_token()
    # start_time = time.time()  # 记录开始时间

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': query}
        ],
        temperature=tem,
        max_tokens=max,
        stream=True  # 开启流式输出
    )

    result = ""  # 创建一个空字符串来保存流式输出的结果

    for chunk in response:
        # 确保字段存在
        if 'choices' in chunk and 'delta' in chunk['choices'][0]:
            chunk_msg = chunk['choices'][0]['delta'].get('content', '')
            result += chunk_msg  # 将输出内容附加到结果字符串上

            if stream_true:
                # print(chunk_msg, end='', flush=True)
                time.sleep(0.05)

    return result  # 返回流式输出的完整结果


@Client.on_message(command('chatgpt'))
async def chatgpt(client: Client, message: Message):
    """与chatgpt对话"""
    cmd, args = Parameters.get(message)
    query_str = args
    await message.edit_text("🌍正在询问chatgpt,请稍后...")
    full_result = fakeopen_api(query_str, 5000, True, 0.8)

    result_text = f"🔎 | **ChatGPT** | `回复`\n{full_result}"
    await message.edit_text(
        text=result_text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )
