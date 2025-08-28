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
CHECK_UPGRADES_PER_CYCLE = 2

DATA_FILEPATH = constants.WORK_DIRPATH / "star_gifts.json"
DATA_SAVER_DELAY = 2.
NOTIFY_CHAT_ID = -1002452764624  # https://t.me/gifts_detector
NOTIFY_UPGRADES_CHAT_ID = -1002751596218  # https://t.me/gifts_upgrades_detector
                                          # Если не нужны апгрейды, установите в `None` или `9`.
                                          # Дополнительно: боты не могут проверять апгрейды подарков,
                                          # Telegram выдаст [400 BOT_METHOD_INVALID]
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
💎 Цена: {price} ⭐️
♻️ Конвертированная цена: {convert_price} ⭐️
{require_premium_or_user_limited}
"""

NOTIFY_TEXT_TITLES = {
    True: "🔥 Появился новый лимитированный подарок",
    False: "❄️ Появился новый подарок"
}

NOTIFY_TEXT_TOTAL_AMOUNT = "\n🎯 Всего: {total_amount}"
NOTIFY_TEXT_AVAILABLE_AMOUNT = "\n❓ Доступно: {available_amount} ({same_str}{available_percentage}%, обновлено {updated_datetime} UTC)\n"
NOTIFY_TEXT_SOLD_OUT = "\n⏰ Полностью распродано за {sold_out}\n"
NOTIFY_TEXT_REQUIRE_PREMIUM_OR_USER_LIMITED = "\n{emoji} {require_premium}{separator}{user_limited}\n"
NOTIFY_TEXT_REQUIRE_PREMIUM_OR_USER_LIMITED_EMOJI = "✨"
NOTIFY_TEXT_REQUIRE_PREMIUM = "<b>Только для Premium</b>"
NOTIFY_TEXT_USER_LIMITED = "<b>{user_limited} на пользователя</b>"
NOTIFY_TEXT_REQUIRE_PREMIUM_AND_USER_LIMITED_SEPARATOR = " | "

NOTIFY_UPGRADES_TEXT = "Подарок можно улучшить! (<code>{id}</code>)"
