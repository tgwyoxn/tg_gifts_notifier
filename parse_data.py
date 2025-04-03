from pyrogram import Client, raw
from pyrogram.file_id import FileId, FileType

import typing

from star_gifts_data import StarGiftData


@typing.overload
async def get_all_star_gifts(
    client: Client,
    hash: typing.Literal[None] = ...
) -> tuple[int, dict[int, StarGiftData]]: ...

@typing.overload
async def get_all_star_gifts(
    client: Client,
    hash: int
) -> tuple[int, dict[int, StarGiftData] | None]: ...

async def get_all_star_gifts(
    client: Client,
    hash: int | None = None
) -> tuple[int, dict[int, StarGiftData] | None]:
    r: raw.types.payments.StarGifts | raw.types.payments.StarGiftsNotModified = await client.invoke(  # type: ignore
        raw.functions.payments.GetStarGifts(  # type: ignore
            hash = hash or 0
        )
    )

    if isinstance(r, raw.types.payments.StarGiftsNotModified):  # type: ignore
        return (
            hash,  # type: ignore
            None
        )

    r_gifts: list[raw.types.StarGift] = r.gifts  # type: ignore

    all_star_gifts_dict: dict[int, StarGiftData] = {
        star_gift_raw.id: StarGiftData(
            id = star_gift_raw.id,
            number = i,
            sticker_file_id = FileId(
                file_type = FileType.DOCUMENT,
                dc_id = star_gift_raw.sticker.dc_id,  # type: ignore
                media_id = star_gift_raw.sticker.id,  # type: ignore
                access_hash = star_gift_raw.sticker.access_hash,  # type: ignore
                file_reference = star_gift_raw.sticker.file_reference  # type: ignore
            ).encode(),
            sticker_file_name = next(
                (
                    attr.file_name
                    for attr in star_gift_raw.sticker.attributes  # type: ignore
                    if isinstance(attr, raw.types.DocumentAttributeFilename)  # type: ignore
                ),
                f"{star_gift_raw.id}.tgs"  # hardcode
            ),
            price = star_gift_raw.stars,
            convert_price = star_gift_raw.convert_stars,
            available_amount = star_gift_raw.availability_remains or 0,
            total_amount = star_gift_raw.availability_total or 0,
            is_limited = star_gift_raw.limited or False
        )
        for i, star_gift_raw in enumerate(sorted(
            r_gifts,
            key = lambda star_gift_raw: star_gift_raw.id,
            reverse = False
        ), 1)
    }

    return (
        r.hash,  # type: ignore
        all_star_gifts_dict
    )
