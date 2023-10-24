import os

from pyrogram.methods.utilities.idle import idle

from core import app
from tools.initializer import init_logger
from tools.sessions import session


# 加在plugins下所有的插件
def load_plugins():
    # 获取当前脚本的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # 插件目录的相对路径
    plugins_directory = "plugins"

    # 完整插件目录的路径
    plugins_directory_path = os.path.join(current_directory, plugins_directory)

    # 遍历插件目录下的所有文件
    for root, dirs, files in os.walk(plugins_directory_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # 构建模块的完整路径
                module_path = os.path.splitext(os.path.join(root, file).replace(os.path.sep, "."))[0]

                # 动态导入模块
                plugin_module = __import__(module_path, fromlist=["__plugin__"])

                # 获取插件信息
                plugin_info = plugin_module.__plugin__

                # 添加插件到 Pyrogram 客户端
                app.add_handler(plugin_module)


async def main():
    init_logger()
    load_plugins()
    await app.start()
    await idle()
    await session.close()
    await app.stop()


if __name__ == '__main__':
    app.run(main())
