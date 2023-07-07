from .custom import command, CMDS_DATA, CMDS_PREFIX
from pyrogram import Client
from tools.helpers import BotConfigParser
bot_config = BotConfigParser().get_config()
pyrogram_section = bot_config["pyrogram"]
api_id = pyrogram_section.get("api_id")
api_hash = pyrogram_section.get("api_hash")
app = Client(
    "./data/app",
    api_id=api_id,
    api_hash=api_hash,
    plugins=dict(root="plugins"),
    # proxy={
    #     # "socks4", "socks5" and "http" are supported
    #     "scheme": "socks5",
    #     "hostname": "127.0.0.1",
    #     "port": 7890,
    #     #  "username": "username",
    #     #  "password": "password"
    # },
)


__all__ = (
    'app',
    'command',
    'CMDS_DATA',
    'CMDS_PREFIX',
)
