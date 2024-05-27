# 请求genshinvoice.top的api
import asyncio
import logging
import time
from datetime import datetime, timedelta, timezone

import aiohttp


class GenshinTTS:
    def __init__(self):
        self.config = {
            "speaker": "神里绫华",
            "format": "wav",
            "length": "1.25",
            "noise": "0.2",
            "noisew": "0.9"
        }

    def get_bj_time(self, type=0):
        """获取北京时间

        Args:
            type (int, str): 返回时间类型. 默认为 0.
                0 返回数据：年-月-日 时:分:秒
                1 返回数据：年-月-日
                2 返回数据：当前时间的秒
                3 返回数据：自1970年1月1日以来的秒数
                4 返回数据：返回自1970年1月1日以来的毫秒数 % 100
                5 返回数据：当前 时点分
                6 返回数据：当前时间的 时, 分

        Returns:
            str: 返回指定格式的时间字符串
            int, int
        """
        if type == 0:
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)  # 获取当前 UTC 时间
            SHA_TZ = timezone(
                timedelta(hours=8),
                name='Asia/Shanghai',
            )
            beijing_now = utc_now.astimezone(SHA_TZ)  # 将 UTC 时间转换为北京时间
            fmt = '%Y-%m-%d %H:%M:%S'
            now_fmt = beijing_now.strftime(fmt)
            return now_fmt
        elif type == 1:
            now = datetime.now()  # 获取当前时间
            year = now.year  # 获取当前年份
            month = now.month  # 获取当前月份
            day = now.day  # 获取当前日期

            return str(year) + "-" + str(month) + "-" + str(day)
        elif type == 2:
            now = time.localtime()  # 获取当前时间

            # hour = now.tm_hour   # 获取当前小时
            # minute = now.tm_min  # 获取当前分钟
            second = now.tm_sec  # 获取当前秒数

            return str(second)
        elif type == 3:
            current_time = time.time()  # 返回自1970年1月1日以来的秒数

            return str(current_time)
        elif type == 4:
            current_time = time.time()  # 返回自1970年1月1日以来的秒数
            current_milliseconds = int(current_time * 1000)  # 毫秒为单位
            tgt_time = current_milliseconds % 100  # 用于生成音频文件名

            return str(tgt_time)
        elif type == 5:
            now = time.localtime()  # 获取当前时间

            hour = now.tm_hour  # 获取当前小时
            minute = now.tm_min  # 获取当前分钟

            return str(hour) + "点" + str(minute) + "分"
        elif type == 6:
            now = time.localtime()  # 获取当前时间

            hour = now.tm_hour  # 获取当前小时
            minute = now.tm_min  # 获取当前分钟

            return hour, minute

    async def genshinvoice_top_api(self, text):
        url = 'https://genshinvoice.top/api'

        genshinvoice_top = self.config

        params = {
            'speaker': genshinvoice_top['speaker'],
            'text': text,
            'format': genshinvoice_top['format'],
            'length': genshinvoice_top['length'],
            'noise': genshinvoice_top['noise'],
            'noisew': genshinvoice_top['noisew']
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response = await response.read()
                    voice_tmp_path = './out/genshinvoice_top_' + self.get_bj_time(4) + '.wav'
                    with open(voice_tmp_path, 'wb') as f:
                        f.write(response)

                    return voice_tmp_path
        except aiohttp.ClientError as e:
            logging.error(f'genshinvoice.top请求失败: {e}')
        except Exception as e:
            logging.error(f'genshinvoice.top未知错误: {e}')

        return None


async def main():
    genshin_tts = GenshinTTS()
    await genshin_tts.genshinvoice_top_api("你好 原神")


if __name__ == '__main__':
    asyncio.run(main())
