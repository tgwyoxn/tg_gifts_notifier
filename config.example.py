import logging

import constants


SESSION_NAME = "account"

API_ID = 1234
API_HASH = "1234"

BOT_TOKENS = [
    "1234:abcd",
    "2345:bcda",
    "3456:cdef",
]


CHECK_INTERVAL = 90.

DATA_FILEPATH = constants.WORK_DIRPATH / "star_gifts.json"
DATA_SAVER_DELAY = 5.
NOTIFY_CHAT_ID = -1002452764624  # https://t.me/gifts_detector
NOTIFY_AFTER_STICKER_DELAY = 1.
NOTIFY_AFTER_TEXT_DELAY = 2.
TIMEZONE = "UTC"
CONSOLE_LOG_LEVEL = logging.DEBUG
FILE_LOG_LEVEL = logging.INFO
HTTP_REQUEST_TIMEOUT = 5.


NOTIFY_TEXT = """\
{title}

№ {number} (<code>{id}</code>)
{total_amount}{available_amount}
💎 Price: {price} ⭐️
♻️ Convert price: {convert_price} ⭐️
"""

NOTIFY_TEXT_TITLES = {
    True: "🔥 A new limited gift has appeared",
    False: "❄️ A new gift has appeared"
}

NOTIFY_TEXT_TOTAL_AMOUNT: str = "\n🎯 Total amount: {total_amount}"
NOTIFY_TEXT_AVAILABLE_AMOUNT: str = "\n❓ Available amount: {available_amount} ({same_str}{available_percentage}%, updated at {updated_datetime} UTC)\n"
