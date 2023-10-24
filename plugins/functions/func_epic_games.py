import contextlib
import os
import sys
from datetime import datetime

import aiohttp
from pyrogram import Client
from pyrogram.types import Message
from pytz import timezone

from core import command


async def get_epic_games():
    epic_url = "https://www.epicgames.com/graphql"
    headers = {
        "Referer": "https://www.epicgames.com/store/zh-CN/",
        "Content-Type": "application/json; charset=utf-8",
    }
    data = {
        "query": "query searchStoreQuery($allowCountries: String, $category: String, $count: Int, $country: String!, "
                 "$keywords: String, $locale: String, $namespace: String, $sortBy: String, $sortDir: String, $start: Int, "
                 "$tag: String, $withPrice: Boolean = false, $withPromotions: Boolean = false) {\n Catalog {\n "
                 "searchStore(allowCountries: $allowCountries, category: $category, count: $count, country: $country, "
                 "keywords: $keywords, locale: $locale, namespace: $namespace, sortBy: $sortBy, sortDir: $sortDir, "
                 "start: $start, tag: $tag) {\n elements {\n title\n id\n namespace\n description\n effectiveDate\n "
                 "keyImages {\n type\n url\n }\n seller {\n id\n name\n }\n productSlug\n urlSlug\n url\n items {\n id\n "
                 "namespace\n }\n customAttributes {\n key\n value\n }\n categories {\n path\n }\n price(country: "
                 "$country) @include(if: $withPrice) {\n totalPrice {\n discountPrice\n originalPrice\n voucherDiscount\n "
                 "discount\n currencyCode\n currencyInfo {\n decimals\n }\n fmtPrice(locale: $locale) {\n originalPrice\n "
                 "discountPrice\n intermediatePrice\n }\n }\n lineOffers {\n appliedRules {\n id\n endDate\n "
                 "discountSetting {\n discountType\n }\n }\n }\n }\n promotions(category: $category) @include(if: "
                 "$withPromotions) {\n promotionalOffers {\n promotionalOffers {\n startDate\n endDate\n discountSetting {"
                 "\n discountType\n discountPercentage\n }\n }\n }\n upcomingPromotionalOffers {\n promotionalOffers {\n "
                 "startDate\n endDate\n discountSetting {\n discountType\n discountPercentage\n }\n }\n }\n }\n }\n paging "
                 "{\n count\n total\n }\n }\n }\n}\n",
        "variables": {
            "allowCountries": "CN",
            "category": "freegames",
            "count": 1000,
            "country": "CN",
            "locale": "zh-CN",
            "sortBy": "effectiveDate",
            "sortDir": "asc",
            "withPrice": True,
            "withPromotions": True,
        },
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=epic_url, json=data, headers=headers) as response:
            # 检查响应状态
            if response.status == 200:
                response_data = await response.json()
                print("POST 请求成功，响应数据：")
                print(response_data["data"]["Catalog"]["searchStore"]["elements"])
                return response_data["data"]["Catalog"]["searchStore"]["elements"]
            else:
                print(f"POST 请求失败，状态码：{response.status}")
                return f"Post请求失败, url:{epic_url},error: {response.text()}"


def parse_game_info(game):
    game_name = game["title"]
    game_corp = game["seller"]["name"]
    game_price = game["price"]["totalPrice"]["fmtPrice"]["originalPrice"]
    game_promotions = game["promotions"]["promotionalOffers"]
    upcoming_promotions = game["promotions"]["upcomingPromotionalOffers"]
    if not game_promotions and upcoming_promotions:
        raise ValueError  # 促销即将上线，跳过
    if (
            game_promotions[0]["promotionalOffers"][0]["discountSetting"]["discountType"]
            == "PERCENTAGE"
            and game_promotions[0]["promotionalOffers"][0]["discountSetting"][
        "discountPercentage"
    ]
            != 0
    ):
        raise ValueError  # 不免费，跳过
    game_thumbnail, game_dev, game_pub = None, None, None
    for image in game["keyImages"]:
        game_thumbnail = image["url"] if image["type"] == "Thumbnail" else None
    for pair in game["customAttributes"]:
        game_dev = pair["value"] if pair["key"] == "developerName" else game_corp
        game_pub = pair["value"] if pair["key"] == "publisherName" else game_corp
    game_desp = game["description"]
    end_date_iso = game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0][
                       "endDate"
                   ][:-1]
    end_date = (
        datetime.fromisoformat(end_date_iso)
        .replace(tzinfo=timezone("UTC"))
        .astimezone(timezone("Asia/Chongqing"))
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    # API 返回不包含游戏商店 URL，此处自行拼接，可能出现少数游戏 404
    game_url = (
        f"https://www.epicgames.com/store/zh-CN/p/{game['productSlug'].replace('/home', '')}"
        if game["productSlug"] else "暂无链接"
    )
    msg = f"**FREE now :: {game_name} ({game_price})**\n\n{game_desp}\n\n"
    msg += (
        f"游戏由 {game_pub} 发售，"
        if game_dev == game_pub
        else f"游戏由 {game_dev} 开发、{game_pub} 出版，"
    )
    msg += f"将在 **{end_date}** 结束免费游玩，戳下面的链接领取吧~\n{game_url}"

    return msg, game_thumbnail


"""
data/command.yml

epic:
  cmd: epic
  format: epic <无>
  usage: 获取Epic Games喜加一限免

"""


@Client.on_message(command("epic"))
async def epic_games(message: Message):
    try:
        games = await get_epic_games()
    except Exception as e:
        return await message.edit_text(
            f"请求 Epic Store API 错误：{str(sys.exc_info()[0])}" + "\n" + str(e)
        )
    if not games:
        return await message.edit_text("Epic 可能又抽风啦，请稍后再试（")
    for game in games:
        try:
            msg, game_thumbnail = parse_game_info(game)
            if game_thumbnail:
                async with aiohttp.ClientSession() as session:
                    async with session.get(game_thumbnail) as response:
                        if response.status == 200:
                            async with response.content as content:
                                with open('epic.jpg', 'wb') as file:
                                    while True:
                                        chunk = await content.read(1024)
                                        if not chunk:
                                            break
                                        file.write(chunk)
                                print(f"Image saved to epic.jpg")
                        else:
                            print(f"Failed to fetch image from {game_thumbnail}")
                try:
                    await message.reply_photo(
                        "epic.jpg",
                        caption=msg,
                        quote=False,
                        reply_to_message_id=message.reply_to_top_message_id,
                    )
                except Exception:
                    await message.reply(
                        msg,
                        quote=False,
                        reply_to_message_id=message.reply_to_top_message_id,
                    )
                safe_remove("epic.jpg")
            else:
                await message.reply(msg, quote=False)
        except (TypeError, IndexError):
            pass
        except ValueError:
            continue
        except Exception as e:
            return await message.edit_text(
                f"获取 Epic 信息错误：{str(sys.exc_info()[0])}" + "\n" + str(e)
            )
    await message.delete()


def safe_remove(name: str) -> None:
    with contextlib.suppress(FileNotFoundError):
        os.remove(name)
