from datetime import datetime

import aiohttp
import asyncio
import aiofiles


async def start_download(url):
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,ja;q=0.6',
        'Origin': 'https://y2down.cc',
        'Referer': 'https://y2down.cc/',
        'Sec-Ch-Ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': 'macOS',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print("start download successful")
                return data
            else:
                print(f"Error: {response.status}")
                return None


async def query_progress(download_id: str):
    url = f"https://p.oceansaver.in/ajax/progress.php?id={download_id}"
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,ja;q=0.6',
        'Origin': 'https://y2down.cc',
        'Referer': 'https://y2down.cc/',
        'Sec-Ch-Ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': 'macOS',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print(f"Error: {response.status}")
                return None


async def download_video(file_url: str, save_path: str):
    url = file_url
    headers = {
        'Accept-Language': 'zh,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,ja;q=0.6',
        'Referer': 'https://y2down.cc/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                content_type = response.headers.get('Content-Type')
                if 'application/octet-stream' or 'video' in content_type:
                    filename = response.headers.get('Content-Disposition')
                    if filename:
                        filename = filename.split('filename=')[-1].strip()[1:-1]
                    else:
                        filename = f'video-{formatted_time}.mp4'

                    file_path = f"{save_path}/{filename}"

                    async with aiofiles.open(file_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            await f.write(chunk)

                    return file_path

                else:
                    print("The response is not a video.")
                    return None
            else:
                print(f"Error: {response.status}")
                return None


async def main(youtube_url: str):
    url = f"https://loader.to/ajax/download.php?format=4k&url={youtube_url}"
    data = await start_download(url)
    if data:
        print(data)
        download_id = data["id"]
        # check if success
        while True:
            progress = await query_progress(download_id)
            if progress['progress'] != 1000:
                print("Please wait, video is still converting...")
                await asyncio.sleep(5)
            else:
                print("video converted successfully!")
                print(progress)
                break
        save_dir = "../../videos"
        await download_video(progress['download_url'], save_dir)
        print("Video download successfully")

    else:
        print("Failed to fetch data")


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=KAUD9IejGj0'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url))
