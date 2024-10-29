from pyrogram import Client, types
from io import BytesIO

import json
import math
import asyncio
import typing

import config


null_str: str = ""


async def detector(app: Client, callback: typing.Callable) -> None:
    while True:
        print("Loop started")

        await app.start()

        old_star_gifts_raw: list[dict]

        try:
            with open("star_gifts.json", "r") as file:
                old_star_gifts_raw = json.load(file)

        except FileNotFoundError:
            old_star_gifts_raw = []

        old_star_gifts_raw_dict: dict[int, dict] = {
            star_gift_raw["id"]: star_gift_raw
            for star_gift_raw in old_star_gifts_raw
        }

        all_star_gifts_raw: list[dict] = [
            json.loads(json.dumps(
                star_gift,
                indent = 4,
                default = types.Object.default,
                ensure_ascii = False
            ))
            for star_gift in await app.get_star_gifts()
        ]

        all_star_gifts_raw_dict: dict[int, dict] = {
            star_gifts_raw["id"]: star_gifts_raw
            for star_gifts_raw in all_star_gifts_raw
        }

        new_star_gifts_raw: dict[int, dict] = {
            key: value
            for key, value in all_star_gifts_raw_dict.items()
            if key not in old_star_gifts_raw_dict
        }

        if new_star_gifts_raw:
            print("New star gifts found:", len(new_star_gifts_raw))

            all_star_gifts_ids: list[int] = list(all_star_gifts_raw_dict.keys())
            all_star_gifts_amount: int = len(all_star_gifts_ids)

            for star_gift_id, star_gift_raw in new_star_gifts_raw.items():
                star_gift_raw["number"] = all_star_gifts_amount - all_star_gifts_ids.index(star_gift_id)

            for star_gift_id, star_gift_raw in sorted(
                new_star_gifts_raw.items(),
                key = lambda it: it[1]["number"]
            ):
                await callback(
                    app,
                    star_gift_raw
                )

            with open("star_gifts.json", "w") as file:
                json.dump(
                    obj = all_star_gifts_raw,
                    fp = file,
                    indent = 4,
                    default = types.Object.default,
                    ensure_ascii = False
                )

        await app.stop()

        await asyncio.sleep(config.CHECK_INTERVAL)


def pretty_int(number: int) -> str:
    return "{:,}".format(number)


def pretty_float(number: float, get_is_same: bool=False) -> tuple[str, bool] | str:
    number_str: str = "{:.1g}".format(float(number))

    if get_is_same:
        return (
            number_str,
            float(number_str) == number
        )

    return number_str


async def notify(app: Client, star_gift_raw: dict) -> None:
    is_limited: bool = star_gift_raw["is_limited"]

    binary: BytesIO = await app.download_media(
        message = star_gift_raw["sticker"]["file_id"],
        in_memory = True
    )

    binary.name = "{}.{}".format(
        star_gift_raw["id"],
        star_gift_raw["sticker"]["file_name"].split(".")[-1]
    )

    sticker_message: types.Message = await app.send_sticker(
        chat_id = config.NOTIFY_CHAT_ID,
        sticker = binary
    )

    await asyncio.sleep(config.NOTIFY_AFTER_STICKER_DELAY)

    available_percentage, available_percentage_is_same = pretty_float(
        number = math.ceil(star_gift_raw["available_amount"] / star_gift_raw["total_amount"] * 100 * 100) / 100,
        get_is_same = True
    )

    await app.send_message(
        chat_id = config.NOTIFY_CHAT_ID,
        text = config.NOTIFY_TEXT.format(
            title = config.NOTIFY_TEXT_TITLES[is_limited],
            number = star_gift_raw.pop("number"),
            id = star_gift_raw["id"],
            total_amount = (
                config.NOTIFY_TEXT_TOTAL_AMOUNT.format(
                    total_amount = pretty_int(star_gift_raw["total_amount"])
                )
                if is_limited
                else
                null_str
            ),
            available_amount = (
                config.NOTIFY_TEXT_AVAILABLE_AMOUNT.format(
                    available_amount = pretty_int(star_gift_raw["available_amount"]),
                    same_str = (
                        ""
                        if available_percentage_is_same
                        else
                        "~"
                    ),
                    available_percentage = available_percentage
                )
                if is_limited
                else
                null_str
            ),
            price = pretty_int(star_gift_raw["price"]),
            convert_price = pretty_int(star_gift_raw["convert_price"])
        ),
        reply_to_message_id = sticker_message.id
    )

    await asyncio.sleep(config.NOTIFY_AFTER_TEXT_DELAY)


async def main() -> None:
    app: Client = Client(
        name = config.SESSION_NAME,
        api_id = config.API_ID,
        api_hash = config.API_HASH
    )

    await detector(
        app = app,
        callback = notify
    )


asyncio.run(main())
