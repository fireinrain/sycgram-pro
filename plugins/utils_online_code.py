from aiohttp import ClientSession
from pyrogram import Client
from pyrogram.types import Message

from core import command
from tools.helpers import Parameters
from tools.sessions import session

codeType = {
    "asm": ["assembly", "asm"],
    "c": ["c", "c"],
    "cpp": ["cpp", "cpp"],
    "c#": ["csharp", "cs"],
    "go": ["go", "go"],
    "java": ["java", "java"],
    "js": ["javascript", "js"],
    "kt": ["kotlin", "kt"],

    "py": ["python", "py"],
    "php": ["php", "php"],
    "rust": ["rust", "rs"],
    "sh": ["bash", "sh"],
    "ts": ["typescript", "ts"],
}


# https://onecompiler.com/c


async def run_code(codes: str, client: ClientSession):
    codes_list = codes.split(" ", 1)
    language_type = codes_list[0]
    code_source = codes_list[1]

    supported_language = [i[1] for i in codeType.values()]
    if language_type not in supported_language:
        return "输入有误\n目前仅支持asm/c/cpp/c#/go/java/js/kt/py/php/rust/sh/ts"

    data_json = {
        "files": [{"name": f"main.{codeType[language_type][1]}", "content": code_source}],
        "stdin": "",
        "command": "",
    }
    # cookie 可能失效
    headers = {
        "Authorization": "Token 0123456-789a-bcde-f012-3456789abcde",
        "Origin": "https://glot.io",
        "Content-Type": "application/json",
        "Referer": f"https://glot.io/new/{codeType[language_type][1]}",
        "Cookie": "_SESSION=wt+lfkRPpAp1NZ5US7KhBb4SYzuixAoPkVRm0+ub/e+tz6EQMdCgjPPB5OaxudjLSkw6hiZIJPfAFwjdH9QU2N0LEfnh6NzbXTMeyTgu3s65UpV+rPXP/h4exogT8L/zfyl7NIN1Yd9SD4zXfkcYQCbZS04orUF5ZXJ4l8JXRouJmThGX9n0vb+VMzSrGuHBA/C+eEIXJmsQImILtNDKxDmGp6vB4I+nv0b59cfzJUsgS7XcCCn8"
    }
    res = await client.post(
        url=f"https://glot.io/run/{codeType[language_type][0]}?version=latest",
        headers=headers,
        json=data_json,
    )
    if res.status != 200:
        return "请求失败了呐~~~"
    if res.json()["stdout"] == "":
        return res.json()["stderr"].strip()
    return f"<b>>>></b> <code>{code_source}</code> \n{res.json()['stdout']}"


"""
data/command.yml

runcode:
  cmd: runcode
  format: runcode <编程语言后缀名> <代码>
  usage: 在线运行代码并展示结果
"""


@Client.on_message(command("runcode"))
async def online_code(client: Client, message: Message):
    cmd, args = Parameters.get(message)
    s = session
    results = await run_code(args, s)
    await message.edit_text(results)
