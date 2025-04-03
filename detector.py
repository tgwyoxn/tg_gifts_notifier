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
NEW_GIFTS_QUEUE_T = asyncio.Queue[StarGiftData]
UPDATE_GIFTS_QUEUE_T = asyncio.Queue[tuple[StarGiftData, StarGiftData]]


if not config.BOT_TOKENS:
    raise ValueError("BOT_TOKENS is empty")

BOTS_AMOUNT = len(config.BOT_TOKENS)


_http_transport = AsyncHTTPTransport()

BOT_HTTP_CLIENTS = cycle([
    AsyncClient(
        base_url = f"https://api.telegram.org/bot{bot_token}",
        transport = _http_transport
    )
    for bot_token in config.BOT_TOKENS
])


STAR_GIFTS_DATA = StarGiftsData.load()
last_star_gifts_data_saved_time: int | None = None


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
    new_gifts_queue: NEW_GIFTS_QUEUE_T | None = None,
    update_gifts_queue: UPDATE_GIFTS_QUEUE_T | None = None
) -> None:
    if new_gifts_queue is None and update_gifts_queue is None:
        raise ValueError("At least one of new_gifts_queue or update_gifts_queue must be provided")

    while True:
        print(f"[{utils.get_current_datetime(timezone)}] Checking for new gifts / updates...")

        if not app.is_connected:
            await app.start()

        all_star_gifts_dict = {
            star_gift_id: star_gift
            for star_gift_id, star_gift in (await get_all_star_gifts(
                client = app,
                hash = None
            ))[1].items()
        }

        old_star_gifts = STAR_GIFTS_DATA.star_gifts

        old_star_gifts_dict = {
            star_gift.id: star_gift
            for star_gift in old_star_gifts
        }

        new_star_gifts = {
            star_gift_id: star_gift
            for star_gift_id, star_gift in all_star_gifts_dict.items()
            if star_gift_id not in old_star_gifts_dict
        }

        if new_star_gifts and new_gifts_queue:
            for star_gift_id, star_gift in new_star_gifts.items():
                new_gifts_queue.put_nowait(star_gift)

        if update_gifts_queue:
            for star_gift_id, old_star_gift in old_star_gifts_dict.items():
                new_star_gift = all_star_gifts_dict[star_gift_id]
                new_star_gift.message_id = old_star_gift.message_id

                if new_star_gift.available_amount < old_star_gift.available_amount:
                    update_gifts_queue.put_nowait((old_star_gift, new_star_gift))

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


async def process_new_gifts(app: Client, new_gifts_queue: NEW_GIFTS_QUEUE_T) -> None:
    while True:
        star_gift = await new_gifts_queue.get()

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

        await star_gifts_data_saver(star_gift)

        new_gifts_queue.task_done()

        await asyncio.sleep(config.NOTIFY_AFTER_TEXT_DELAY)


async def process_update_gifts(update_gifts_queue: UPDATE_GIFTS_QUEUE_T) -> None:
    while True:
        new_star_gifts: list[StarGiftData] = []

        while True:
            try:
                _, new_star_gift = update_gifts_queue.get_nowait()
                new_star_gifts.append(new_star_gift)

            except asyncio.QueueEmpty:
                break

        if not new_star_gifts:
            await asyncio.sleep(0.1)

            continue

        for new_star_gift in new_star_gifts:
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

        await star_gifts_data_saver(new_star_gifts)

        update_gifts_queue.task_done()


star_gifts_data_saver_lock = asyncio.Lock()

async def star_gifts_data_saver(star_gifts: StarGiftData | list[StarGiftData]) -> None:
    global STAR_GIFTS_DATA, last_star_gifts_data_saved_time

    async with star_gifts_data_saver_lock:
        if not isinstance(star_gifts, list):
            star_gifts = [star_gifts]

        for star_gift in star_gifts:
            found = False

            for i, old_star_gift in enumerate(STAR_GIFTS_DATA.star_gifts):
                if old_star_gift.id == star_gift.id:
                    STAR_GIFTS_DATA.star_gifts[i] = star_gift
                    found = True

                    break

            if not found:
                for i, old_star_gift in enumerate(STAR_GIFTS_DATA.star_gifts):
                    if star_gift.id < old_star_gift.id:
                        STAR_GIFTS_DATA.star_gifts.insert(i, star_gift)
                        found = True

                        break

            if not found:
                STAR_GIFTS_DATA.star_gifts.append(star_gift)

        if last_star_gifts_data_saved_time is None or last_star_gifts_data_saved_time + config.DATA_SAVER_DELAY < utils.get_current_timestamp():
            STAR_GIFTS_DATA.save()

            last_star_gifts_data_saved_time = utils.get_current_timestamp()

            print("\t", f"[{utils.get_current_datetime(timezone)}] Saved star gifts to file")


async def main() -> None:
    app = Client(
        name = config.SESSION_NAME,
        api_id = config.API_ID,
        api_hash = config.API_HASH
    )

    new_gifts_queue = NEW_GIFTS_QUEUE_T()
    update_gifts_queue = UPDATE_GIFTS_QUEUE_T()

    asyncio.create_task(
        process_new_gifts(
            app = app,
            new_gifts_queue = new_gifts_queue
        )
    )

    asyncio.create_task(
        process_update_gifts(
            update_gifts_queue = update_gifts_queue
        )
    )

    await detector(
        app = app,
        new_gifts_queue = new_gifts_queue,
        update_gifts_queue = update_gifts_queue
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        STAR_GIFTS_DATA.save()
