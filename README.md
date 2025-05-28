# TG Gifts Notifier

## Overview

TG Gifts Notifier is a tool designed to notify users about new gifts available on the Telegram platform. It helps users stay updated and never miss out on any gifts.

Our Telegram Channel — [Gifts Detector](https://t.me/gifts_detector)

## Features

**Note:** This project requires Python 3.10 or higher to run.

- Real-time notifications
- Easy setup and configuration
- Customizable notification settings

## Installation

To install TG Gifts Notifier, follow these steps:

1. Clone the repository:

    ```sh
    git clone https://github.com/arynyklas/tg_gifts_notifier.git
    ```

2. Navigate to the project directory:

    ```sh
    cd tg_gifts_notifier
    ```

3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

To start the notifier, run:

```sh
python detector.py
```

To start the auto buyer, run:

```sh
python auto_buyer.py
```

## Configuration

At first rename `config.example.py` to `config.py`.

Then, you must configure the notifier by editing the `config.py` file.

| Field                      | Type      | Description                                                         |
|-------------------|---------|---------------------------------------------------------------------|
| API_ID                     | Integer   | Your Telegram API ID obtained from my.telegram.org                  |
| API_HASH                   | String    | Your Telegram API Hash corresponding to your API ID                 |
| BOT_TOKENS                 | [String]  | Bot tokens provided by [BotFather](https://t.me/BotFather) of your Telegram bot            |
| CHECK_INTERVAL             | Float     | Time interval (in seconds) between checks for new gifts             |
| DATA_FILEPATH              | String    | Path to the file where the gift data is stored                      |
| NOTIFY_CHAT_ID             | Integer   | Chat ID where notifications are delivered                           |
| NOTIFY_AFTER_STICKER_DELAY | Float     | Delay (in seconds) after sending a sticker before sending a message |
| NOTIFY_AFTER_TEXT_DELAY    | Float     | Delay (in seconds) after sending a message |
| TIMEZONE                   | String    | Timezone for the bot (e.g., "Europe/Moscow")                        |

## Contact

For any questions or feedback, please contact me at [my socials](https://aryn.sek.su/).

---

If you find TG Gifts Notifier useful and would like to support its development, consider making a donation. Your contributions help in maintaining and improving the project.

You can donate via the following methods listed on this [site](https://aryn.sek.su/donates).

Thank you for your support!
