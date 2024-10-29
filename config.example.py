SESSION_NAME: str = "account"

API_ID: int = 1234
API_HASH: str = "1234"


CHECK_INTERVAL: float = 90.

NOTIFY_CHAT_ID: int = -1002452764624  # https://t.me/gifts_detector
NOTIFY_AFTER_STICKER_DELAY: float = 1.
NOTIFY_AFTER_TEXT_DELAY: float = 2.


NOTIFY_TEXT: str = """\
{title}

№ {number} (<code>{id}</code>)
{total_amount}{available_amount}
💎 Price: {price} ⭐️
♻️ Convert price: {convert_price} ⭐️
"""

NOTIFY_TEXT_TITLES: dict[bool, str] = {
    True: "🔥 A new limited gift has appeared",
    False: "❄️ A new gift has appeared"
}

NOTIFY_TEXT_TOTAL_AMOUNT: str = "\n🎯 Total amount: {total_amount}"
NOTIFY_TEXT_AVAILABLE_AMOUNT: str = "\n❓ Available amount: {available_amount} ({same_str}{available_percentage}%)\n"


GIFT_CHAT_IDS: list[int] = [
    794823214,  # @arynme
]

GIFT_TEXT: str = "🎁 Gift №{number} ({id})"
GIFT_HIDE_MY_NAME: bool = True
