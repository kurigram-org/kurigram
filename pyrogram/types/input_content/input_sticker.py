#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations

import io
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.file_id import FileType

from ..object import Object

if TYPE_CHECKING:
    from collections.abc import Callable

    from pyrogram._typing import PathType


class InputSticker(Object):
    """A sticker to be added to a sticker set.

    Parameters:
        sticker (``str`` | ``os.PathLike`` | ``BinaryIO``):
            The added sticker.
            Pass a file_id as string to send a file that exists on the Telegram servers or
            pass a file path as string to upload a new file that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads.

        format (:obj:`~pyrogram.enums.StickerFormat`):
            Format of the added sticker.

        emoji_list (List of ``str``):
            List of 1-20 emoji associated with the sticker.

        mask_position (:obj:`~pyrogram.types.MaskPosition`, *optional*):
            Position where the mask should be placed on faces.
            For mask stickers only.

        keywords (List of ``str``, *optional*):
            List of 0-20 search keywords for the sticker with total length of up to 64 characters.
            For regular and custom emoji stickers only.

    Raises:
        FileNotFoundError: In case a local path doesn't point to an existing file.
        ValueError: In case an animated/video sticker is requested to be uploaded via URL.
    """

    def __init__(
        self,
        sticker: PathType | BinaryIO,
        format: enums.StickerFormat,
        emoji_list: list[str],
        mask_position: types.MaskPosition | None = None,
        keywords: list[str] | None = None,
    ) -> None:
        super().__init__()

        self.sticker = sticker
        self.format = format
        self.emoji_list = emoji_list
        self.mask_position = mask_position
        self.keywords = keywords

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> raw.types.InputStickerSetItem:
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await client.resolve_peer(chat_id)

        file_name = "sticker.png"
        mime_type = "image/png"

        if self.format == enums.StickerFormat.ANIMATED:
            file_name = "sticker.tgs"
            mime_type = "application/x-tgsticker"
        elif self.format == enums.StickerFormat.VIDEO:
            file_name = "sticker.webm"
            mime_type = "video/webm"

        alt = "".join(self.emoji_list)
        mask_coords = self.mask_position.write() if self.mask_position else None
        keywords = ",".join(self.keywords) if self.keywords else None

        if isinstance(self.sticker, io.BytesIO) or Path(self.sticker).is_file():
            uploaded_media = await client.invoke(
                raw.functions.messages.UploadMedia(
                    peer=peer,
                    media=raw.types.InputMediaUploadedDocument(
                        mime_type=mime_type,
                        file=await client.save_file(
                            self.sticker, progress=progress, progress_args=progress_args
                        ),
                        attributes=[
                            raw.types.DocumentAttributeFilename(
                                file_name=file_name,
                            ),
                            raw.types.DocumentAttributeSticker(
                                alt="".join(self.emoji_list),
                                stickerset=raw.types.InputStickerSetEmpty(),
                                mask=self.mask_position is not None,
                                mask_coords=self.mask_position.write()
                                if self.mask_position
                                else None,
                            ),
                        ],
                    ),
                ),
            )

            return raw.types.InputStickerSetItem(
                document=raw.types.InputDocument(
                    id=uploaded_media.document.id,
                    access_hash=uploaded_media.document.access_hash,
                    file_reference=uploaded_media.document.file_reference,
                ),
                emoji=alt,
                mask_coords=mask_coords,
                keywords=keywords,
            )

        if isinstance(self.sticker, os.PathLike):
            raise FileNotFoundError(f"No such file or directory: {self.sticker}")

        if isinstance(self.sticker, str) and re.match("^https?://", self.sticker):
            # TODO: Add support for uploading stickers via URL
            # Maybe via urlib request 🤔🤔🤔
            raise ValueError("Stickers can't be uploaded via URL")

            # if self.format in (enums.StickerFormat.ANIMATED, enums.StickerFormat.VIDEO):
            #     raise ValueError("Animated and video stickers can't be uploaded via URL")

            # uploaded_media = await client.invoke(
            #     raw.functions.messages.UploadMedia(
            #         peer=peer,
            #         media=raw.types.InputMediaDocumentExternal(
            #             url=str(self.sticker),
            #         ),
            #     )
            # )

            # return raw.types.InputStickerSetItem(
            #     document=raw.types.InputDocument(
            #         id=uploaded_media.document.id,
            #         access_hash=uploaded_media.document.access_hash,
            #         file_reference=uploaded_media.document.file_reference,
            #     ),
            #     emoji=alt,
            #     mask_coords=mask_coords,
            #     keywords=keywords,
            # )

        return raw.types.InputStickerSetItem(
            document=utils.get_input_media_from_file_id(self.sticker, FileType.STICKER).id,
            emoji=alt,
            mask_coords=mask_coords,
            keywords=keywords,
        )
