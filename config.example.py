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


CHECK_INTERVAL = 1.
CHECK_UPGRADES_INTERVAL = 0.1
CHECK_UPGRADES_PER_CYCLE = 2

DATA_FILEPATH = constants.WORK_DIRPATH / "star_gifts.json"
DATA_SAVER_DELAY = 2.
NOTIFY_CHAT_ID = -1002452764624  # https://t.me/gifts_detector
NOTIFY_UPGRADES_CHAT_ID = -1002751596218  # https://t.me/gifts_upgrades_detector
                                          # If you don't need upgrades, set it to `None` or `9`.
                                          # Additionally, bots can't check upgrades for gifts,
                                          # Telegram will raise [400 BOT_METHOD_INVALID]
NOTIFY_AFTER_STICKER_DELAY = 1.
NOTIFY_AFTER_TEXT_DELAY = 2.
TIMEZONE = "UTC"
CONSOLE_LOG_LEVEL = logging.DEBUG
FILE_LOG_LEVEL = logging.INFO
HTTP_REQUEST_TIMEOUT = 20.


NOTIFY_TEXT = """\
{title}

№ {number} (<code>{id}</code>)
{total_amount}{available_amount}{sold_out}
💎 Price: {price} ⭐️
♻️ Convert price: {convert_price} ⭐️
"""

NOTIFY_TEXT_TITLES = {
    True: "🔥 A new limited gift has appeared",
    False: "❄️ A new gift has appeared"
}

NOTIFY_TEXT_TOTAL_AMOUNT = "\n🎯 Total amount: {total_amount}"
NOTIFY_TEXT_AVAILABLE_AMOUNT = "\n❓ Available amount: {available_amount} ({same_str}{available_percentage}%, updated at {updated_datetime} UTC)\n"
NOTIFY_TEXT_SOLD_OUT = "\n⏰ Completely sold out in {sold_out}\n"

NOTIFY_UPGRADES_TEXT = "{sticker_url}Gift is upgradable!"
