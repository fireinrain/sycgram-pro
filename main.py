from pyrogram.methods.utilities.idle import idle

from core import app
from tools.initializer import init_logger
from tools.sessions import session


async def main():
    init_logger()
    await app.start()
    await idle()
    await session.close()
    await app.stop()


if __name__ == '__main__':
    app.run(main())
