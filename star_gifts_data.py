from pydantic import BaseModel, Field
from typing_extensions import Self

import simplejson as json

import constants
import config


class BaseConfigModel(BaseModel, extra="ignore"):
    pass


class StarGiftData(BaseConfigModel):
    id: int
    number: int
    sticker_file_id: str
    sticker_file_name: str
    price: int
    convert_price: int
    available_amount: int
    total_amount: int
    is_limited: bool
    message_id: int | None = Field(default=None)


class StarGiftsData(BaseConfigModel):
    star_gifts: list[StarGiftData] = Field(default_factory=list)

    @classmethod
    def load(cls) -> Self:
        try:
            with config.DATA_FILEPATH.open("r", encoding=constants.ENCODING) as file:
                return cls.model_validate(json.load(file))

        except FileNotFoundError:
            return cls()

    def save(self) -> None:
        with config.DATA_FILEPATH.open("w", encoding=constants.ENCODING) as file:
            json.dump(
                obj = self.model_dump(),
                fp = file,
                indent = 4,
                ensure_ascii = True,
                sort_keys = False
            )
