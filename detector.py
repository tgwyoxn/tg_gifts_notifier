from pyrogram import Client, types
from httpx import AsyncClient
from httpx._transports.default import AsyncHTTPTransport
from pytz import timezone as _timezone
from io import BytesIO
from itertools import cycle

import math
import asyncio
import typing

from parse_data import get_all_star_gifts
from star_gifts_data import StarGiftData, StarGiftsData

import utils
import config


timezone = _timezone(config.TIMEZONE)

NULL_STR = ""


STAR_GIFT_RAW_T = dict[str, typing.Any]


if not config.BOT_TOKENS:
    raise ValueError("BOT_TOKENS is empty")

BOTS_AMOUNT = len(config.BOT_TOKENS)


http_transport = AsyncHTTPTransport()

BOT_HTTP_CLIENTS = cycle([
    AsyncClient(
        base_url = f"https://api.telegram.org/bot{bot_token}",
        transport = http_transport
    )
    for bot_token in config.BOT_TOKENS
])


async def bot_send_request(method: str, data: dict[str, typing.Any] | None=None) -> None:
    print(f"Sending request {method} with data: {data}")

    response = None

    for _ in range(BOTS_AMOUNT):
        response = (await next(BOT_HTTP_CLIENTS).post(
            method,
            json = data
        )).json()

        if response.get("ok"):
            return

    raise RuntimeError(f"Failed to send request to Telegram API: {response}")


async def detector(
    app: Client,
    new_callback: typing.Callable[[Client, StarGiftData], typing.Awaitable[None]] | None = None,
    update_callback: typing.Callable[[Client, StarGiftData, StarGiftData], typing.Awaitable[None]] | None = None,
    connect_every_loop: bool = False
) -> None:
    if new_callback is None and update_callback is None:
        raise ValueError("At least one of new_callback or update_callback must be provided")

    star_gifts_data = StarGiftsData.load()

    while True:
        print(f"[{utils.get_current_datetime(timezone)}] Checking for new gifts / updates...")

        if not app.is_connected:
            await app.start()

        old_star_gifts = star_gifts_data.star_gifts

        old_star_gifts_dict = {
            star_gift.id: star_gift
            for star_gift in old_star_gifts
        }

        all_star_gifts_dict = {
            star_gift_id: star_gift
            for star_gift_id, star_gift in (await get_all_star_gifts(
                client = app,
                hash = None
            ))[1].items()
        }

        all_star_gifts = list(all_star_gifts_dict.values())

        new_star_gifts = {
            star_gift_id: star_gift
            for star_gift_id, star_gift in all_star_gifts_dict.items()
            if star_gift_id not in old_star_gifts_dict
        }

        if new_star_gifts and new_callback:
            print("New star gifts found:", len(new_star_gifts))

            for star_gift_id, star_gift in new_star_gifts.items():
                await new_callback(app, star_gift)

                if not star_gift.message_id:
                    raise RuntimeError(f"No \"message_id\" specified for new gift with ID {star_gift_id}")

        if update_callback:
            for star_gift_id, old_star_gift in old_star_gifts_dict.items():
                new_star_gift = all_star_gifts_dict[star_gift_id]
                new_star_gift.message_id = old_star_gift.message_id

                if new_star_gift.available_amount < old_star_gift.available_amount:
                    await update_callback(app, old_star_gift, new_star_gift)

        star_gifts_data.star_gifts = all_star_gifts
        star_gifts_data.save()

        if connect_every_loop:
            await app.stop()

        await asyncio.sleep(config.CHECK_INTERVAL)


def get_notify_text(star_gift: StarGiftData) -> str:
    is_limited = star_gift.is_limited

    available_percentage, available_percentage_is_same = (
        utils.pretty_float(
            math.ceil(star_gift.available_amount / star_gift.total_amount * 100 * 100) / 100,
            get_is_same = True
        )
        if is_limited
        else
        (
            NULL_STR,
            False
        )
    )

    return config.NOTIFY_TEXT.format(
        title = config.NOTIFY_TEXT_TITLES[is_limited],
        number = star_gift.number,
        id = star_gift.id,
        total_amount = (
            config.NOTIFY_TEXT_TOTAL_AMOUNT.format(
                total_amount = utils.pretty_int(star_gift.total_amount)
            )
            if is_limited
            else
            NULL_STR
        ),
        available_amount = (
            config.NOTIFY_TEXT_AVAILABLE_AMOUNT.format(
                available_amount = utils.pretty_int(star_gift.available_amount),
                same_str = (
                    NULL_STR
                    if available_percentage_is_same
                    else
                    "~"
                ),
                available_percentage = available_percentage,
                updated_datetime = utils.get_current_datetime(timezone)
            )
            if is_limited
            else
            NULL_STR
        ),
        price = utils.pretty_int(star_gift.price),
        convert_price = utils.pretty_int(star_gift.convert_price)
    )


async def new_callback(app: Client, star_gift: StarGiftData) -> None:
    binary: BytesIO = await app.download_media(  # type: ignore
        message = star_gift.sticker_file_id,
        in_memory = True
    )

    binary.name = star_gift.sticker_file_name

    sticker_message: types.Message = await app.send_sticker(  # type: ignore
        chat_id = config.NOTIFY_CHAT_ID,
        sticker = binary
    )

    await asyncio.sleep(config.NOTIFY_AFTER_STICKER_DELAY)

    message = await app.send_message(
        chat_id = config.NOTIFY_CHAT_ID,
        text = get_notify_text(star_gift),
        reply_to_message_id = sticker_message.id
    )

    star_gift.message_id = message.id

    await asyncio.sleep(config.NOTIFY_AFTER_TEXT_DELAY)


async def update_callback(app: Client, old_star_gift: StarGiftData, new_star_gift: StarGiftData) -> None:
    if new_star_gift.message_id is None:
        return

    await bot_send_request(
        "editMessageText",
        {
            "chat_id": config.NOTIFY_CHAT_ID,
            "message_id": new_star_gift.message_id,
            "text": get_notify_text(new_star_gift),
            "parse_mode": "HTML"
        }
    )


async def main() -> None:
    app = Client(
        name = config.SESSION_NAME,
        api_id = config.API_ID,
        api_hash = config.API_HASH
    )

    await detector(
        app = app,
        new_callback = new_callback,
        update_callback = update_callback
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
