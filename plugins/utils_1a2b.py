import secrets

from typing import List
from core import command
from pyrogram.types import Message
from pyrogram import Client

from tools.constants import TG_GROUPS

games = {}

"""
data/command.yml
1a2b:
  cmd: 1a2b
  format: -1a2b start/stop/answer/numbers-you-give
  usage: 猜数字游戏
"""


class Game:
    password: List[int]
    times: int

    def __init__(self):
        self.times = 0
        self.gen_password()

    def gen_password(self):
        ans = []
        while len(ans) != 4:
            n = secrets.choice(range(10))
            if n not in ans:
                ans.append(n)
        self.password = ans

    @staticmethod
    def check_input(answer: str):
        numbers = " ".join(answer).split()
        if len(numbers) != 4:
            return False
        data = [0, 0, 0, 0]
        for i in range(4):
            data[i] = int(numbers[i])
        return data

    def check_answer(self, answer: str):
        nums = self.check_input(answer)
        if not nums:
            raise ValueError("Invalid input")
        a, b = 0, 0
        for n in nums:
            if n in self.password:
                if nums.index(n) == self.password.index(n):
                    a += 1
                else:
                    b += 1
        self.times += 1
        return a, b


@Client.on_message(command("1a2b"))
async def play_game_1a2b(cli: Client, message: Message):
    # 只在group中使用
    if message.chat.type in TG_GROUPS:
        return await message.delete()
    command_list = message.text.split(" ")

    if len(command_list) <= 1:
        return await message.edit_text("Please specify a command(start/stop/answer).\n -1A2B numbers to guess the "
                                       "secrete")
    game = games.get(message.chat.id, None)
    if len(command_list) > 2:
        await message.edit_text("Wrong command arguments!")
        return await message.delete()
    if command_list[1] == "start":
        if game:
            return await message.edit_text("Game already started.")
        games[message.chat.id] = Game()
        return await message.edit_text("Game started.")
    if command_list[1] == "stop":
        if not game:
            return await message.edit_text("Game not started.")
        del games[message.chat.id]
        return await message.edit_text("Game stopped.")
    if command_list[1] == "answer":
        if not game:
            return await message.edit_text("Game not started.")
        answer = "".join(map(str, game.password))
        return await message.edit_text(f"The answer is: {answer}\n\nGame over.")
    if game:
        try:
            a, b = game.check_answer(command_list[1])
        except ValueError:
            return await message.edit_text(
                "You need to guess 4 numbers between 0 ~ 9.\nFor example: 1234"
            )
        if a == 4:
            return await message.edit_text("You Win!\n\nGame over.")
        return await message.edit_text("%d:  %dA%dB" % (game.times, a, b))
