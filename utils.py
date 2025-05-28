from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pytz.tzinfo import BaseTzInfo

import logging
import numpy as np
import typing


class StrippingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.msg = record.msg.strip() if isinstance(record.msg, str) else record.msg

        return super().format(record)


if typing.TYPE_CHECKING:
    _LoggerAdapter = logging.LoggerAdapter[logging.Logger]
else:
    _LoggerAdapter = logging.LoggerAdapter

def get_logger(name: str, log_filepath: Path, console_log_level: int=logging.INFO, file_log_level: int=logging.INFO) -> _LoggerAdapter:
    logger = logging.getLogger(name)

    logger.setLevel(min(console_log_level, file_log_level))

    formatter = StrippingFormatter("%(asctime)s - %(star_gift_id)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename = log_filepath.resolve().as_posix(),
        mode = "a",
        maxBytes = 1028 * 1024,  # 1 MB
        backupCount = 1_000,
        encoding = "utf-8"
    )

    file_handler.setLevel(file_log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logging.LoggerAdapter(logger, extra={"star_gift_id": "..."})


def get_current_datetime(timezone: BaseTzInfo) -> str:
    return datetime.now(tz=timezone).strftime("%d-%m-%Y %H:%M:%S")

def get_current_timestamp() -> int:
    return int(datetime.now().timestamp())


def pretty_int(number: int) -> str:
    return "{:,}".format(number)


@typing.overload
def pretty_float(number: float, get_is_same: typing.Literal[True]) -> tuple[str, bool]: ...

@typing.overload
def pretty_float(number: float, get_is_same: typing.Literal[False]) -> str: ...

def pretty_float(number: float, get_is_same: bool=False) -> tuple[str, bool] | str:
    formatted_number = float("{:.1g}".format(float(number)))
    formatted_number_str = np.format_float_positional(formatted_number, trim="-")

    if get_is_same:
        return (
            formatted_number_str,
            formatted_number == number
        )

    return formatted_number_str
