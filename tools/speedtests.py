import json
import os
import platform
from datetime import datetime
from os import path
from time import time
from typing import Any, Dict, Optional, Tuple

from loguru import logger

from .constants import INSTALL_SPEEDTEST, SPEEDTEST_PATH_FILE, SYCGRAM_ERROR
from .helpers import basher


class Speedtester:
    def __init__(self) -> None:
        pass

    async def __aenter__(self):
        self._timer = time()
        logger.info("Speedtest开始 ...")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info(
            f"Speedtest使用了 {time()-self._timer:.5f} 秒结束。")

    async def running(self, cmd: str) -> Tuple[str]:
        """开始执行speedtest

        Args:
            cmd (str, optional): speedtest的完整指令，需要返回json格式.

        Returns:
            Tuple[str]: 第一个值是文本/错误，第二个是图片link
        """
        await self.install_speedtest_cli()
        # 超时报错
        res = await basher(cmd, timeout=60)
        logger.info(f"Speedtest 执行 | {res}")

        try:
            # output result
            self.__output: Dict[str, Any] = json.loads(res.get('output'))
            self.__server: Dict[str, Any] = self.__output.get('server')
        except Exception as e:
            logger.error(e)
            return f"⚠️ Speedtest 错误\n```{res.get('error')}```", ''
        else:
            text = "**Speedtest**\n" \
                f"测速点: {self.get_server()}\n" \
                f"服务商: {self.get_sponsor()}\n" \
                f"上传速度: {self.get_speed('upload')}\n" \
                f"下载速度: {self.get_speed('download')}\n" \
                f"延迟: {self.get_ping('latency')} 抖动: {self.get_ping('jitter')}\n" \
                f"测速时间: {self.get_time()}"
            return text, f"{self.__output.get('result').get('url')}.png"

    async def list_servers_ids(self, cmd: str) -> str:
        await self.install_speedtest_cli()
        res = await basher(cmd, timeout=10)
        logger.info(f"Speedtest 执行 | {res}")
        if not res.get('error'):
            try:
                self.__output: Dict[str, Any] = json.loads(res.get('output'))
            except Exception:
                return "**{SYCGRAM_ERROR}**\n> # `⚠️ 无法获取服务器ids`"
            else:
                tmp = '\n'.join(
                    f"`{k.get('id')}` **|** {k.get('name')} **|** {k.get('location')} {k.get('country')}"
                    for k in self.__output.get('servers')
                )
                return f"**Speedtest节点列表：**\n{tmp}"
        return f"**{SYCGRAM_ERROR}**\n```{res.get('error')}```"

    def get_server(self) -> str:
        location = self.__server.get('location')
        country = self.__server.get('country')
        return f"`{location} {country}`"

    def get_sponsor(self) -> str:
        return f"`{self.__server.get('name')}`"

    def get_speed(self, opt: str) -> str:
        """
        Args:
            opt (str): upload or download

        Returns:
            str: Convert to bits
        """
        def convert(bits) -> str:
            """Unit conversion"""
            power = 1000
            n = 0
            units = {
                0: 'bps',
                1: 'Kbps',
                2: 'Mbps',
                3: 'Gbps',
                4: 'Tbps'
            }
            while bits > power:
                bits = bits / power
                n = n + 1
            return f"{bits:.3f} {units.get(n)}"
        return f"`{convert(self.__output.get(opt).get('bandwidth')*8)}`"

    def get_ping(self, opt: str) -> str:
        return f"`{self.__output.get('ping').get(opt):.3f}`"

    def get_time(self) -> str:
        return f"`{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}`"

    async def install_speedtest_cli(self, opt: str = 'install') -> Optional[str]:
        def exists_file() -> bool:
            return path.exists(SPEEDTEST_PATH_FILE)

        if platform.uname().system != "Linux" or platform.uname().machine not in [
            'i386', 'x86_64', 'armel', 'armhf', 'aarch64',
        ]:
            text = f"不支持的系统 >>> {platform.uname().system} {platform.uname().machine}"
            logger.warning(text)
            return text
        elif opt == 'install':
            if not exists_file():
                await self.__download_file()
                logger.success("第一次使用安装speedtest")
            return
        elif opt == 'update':
            if exists_file():
                os.remove(SPEEDTEST_PATH_FILE)
            await self.__download_file()
            if exists_file():
                text = "更新speedtest成功。"
                logger.success(text)
                return text
            return "更新speedtest失败！"
        else:
            raise ValueError(f'speedtest选项错误 {opt}！')

    async def __download_file(self) -> None:
        await basher(INSTALL_SPEEDTEST, timeout=30)


# import asyncio
# import json
# from datetime import datetime
# from time import time
# from typing import Any, Dict, Tuple

# from loguru import logger

# from .helpers import execute


# class Speedtester:
#     def __init__(self) -> None:
#         pass

#     async def __aenter__(self):
#         self._timer = time()
#         logger.info(f"Speedtest start in {self._timer}")
#         return self

#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         logger.info(
#             f"Speedtest over and takes {time()-self._timer:.5f} seconds.")

#     async def running(self, cmd: str) -> Tuple[str]:
#         """开始执行speedtest

#         Args:
#             cmd (str, optional): speedtest的完整指令，需要返回json格式.
#             Defaults to 'speedtest-cli --share --json'.

#         Returns:
#             Tuple[str]: 第一个值是文本/错误，第二个是图片link
#         """
#         # 超时报错
#         res = await asyncio.wait_for(execute(cmd), timeout=60)
#         logger.info(f"Speedtest Execution | {res}")
#         await logger.complete()

#         if not res.get('error'):
#             if 'list' in cmd:
#                 return res.get('output'), ''

#             try:
#                 # output result
#                 self.__output: Dict[str, Any] = json.loads(res.get('output'))
#                 self.__server: Dict[str, Any] = self.__output.get('server')
#             except (TypeError, AttributeError, json.decoder.JSONDecodeError):
#                 return "⚠️ Unable to get detailed data.", ''

#             else:
#                 text = "**Speedtest**\n" \
#                     f"Server: {self.get_server()}\n" \
#                     f"Sponsor: {self.get_sponsor()}\n" \
#                     f"Upload: {self.get_speed('upload')}\n" \
#                     f"Download: {self.get_speed('download')}\n" \
#                     f"Latency: {self.get_latency()}\n" \
#                     f"Time: {self.get_time()}"
#                 return text, self.__output.get('share')

#         return f"⚠️ Error | {res.get('error')}", ''

#     def get_server(self) -> str:
#         country = self.__server.get('country')
#         cc = self.__server.get('cc')
#         return f"`{country} - {cc}`"

#     def get_sponsor(self) -> str:
#         return f"`{self.__server.get('sponsor')}`"

#     def get_speed(self, option: str) -> str:
#         """
#         Args:
#             option (str): upload or download

#         Returns:
#             str: Convert to bits
#         """
#         return f"`{self.convert(self.__output.get(option))}`"

#     def get_latency(self) -> str:
#         return f"`{self.__server.get('latency')}`"

#     def get_time(self) -> str:
#         return f"`{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}`"

#     @staticmethod
#     def convert(bits) -> str:
#         """Unit conversion"""
#         power = 1024
#         n = 0
#         units = {
#             0: 'bps',
#             1: 'Kbps',
#             2: 'Mbps',
#             3: 'Gbps',
#             4: 'Tbps'
#         }
#         while bits > power:
#             bits = bits / power
#             n = n + 1
#         return f"{bits:.3f} {units.get(n)}"
