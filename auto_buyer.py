from pyrogram import Client
from pyrogram.errors.exceptions import RPCError

from detector import detector, get_notify_text

import config


async def buyer(app: Client, chat_id: int, star_gift_id: int, text: str | None=config.GIFT_TEXT, hide_my_name: bool=config.GIFT_HIDE_MY_NAME) -> None:
    await app.send_star_gift(
        chat_id = chat_id,
        star_gift_id = star_gift_id,
        text = text,
        hide_my_name = hide_my_name
    )

    print("Star gift successfully bought to {}!".format(chat_id))


async def new_callback(app: Client, star_gift_raw: dict) -> None:
    print(get_notify_text(star_gift_raw))

    for chat_id in config.GIFT_CHAT_IDS:
        try:
            await buyer(
                app = app,
                chat_id = chat_id,
                star_gift_id = star_gift_raw["id"]
            )

        except RPCError as ex:
            print("Error while buying star gift to {}:".format(chat_id), str(ex))


async def main() -> None:
    app: Client = Client(
        session_name = config.SESSION_NAME,
        api_id = config.API_ID,
        api_hash = config.API_HASH
    )

    await detector(
        app = app,
        new_callback = new_callback
    )
