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


import pyrogram
from pyrogram import types, enums
from pyrogram._typing import PathType
from typing import BinaryIO
from pyrogram.file_id import FileId, FileType, FileUniqueId, FileUniqueType


class UploadStickerFile:
    async def upload_sticker_file(
        self: pyrogram.Client,
        user_id: int | str,
        sticker: PathType | BinaryIO,
        sticker_format: enums.StickerFormat,
    ) -> types.File:
        """Use this method to set the title of a created sticker set.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
               Unique identifier (int) or username (str) of sticker file owner.

            sticker (``str``):
                File to upload, must fit in a 512x512 square.
                For WEBP stickers the file must be in WEBP or PNG format, which will be converted to WEBP server-side.

            sticker_format (:obj:`~pyrogram.enums.StickerFormat`):
                Format of the sticker.

        Returns:
            :obj:`~pyrogram.types.File`: A uploaded sticker object is returned.
        """
        sticker_set_item = await types.InputSticker(
            sticker=sticker,
            format=sticker_format,
            emoji_list=[],
        ).write(client=self, chat_id=user_id)

        return types.File(
            file_id=FileId(
                file_type=FileType.STICKER,
                dc_id=self.session.dc_id,
                media_id=sticker_set_item.document.id,
                access_hash=sticker_set_item.document.access_hash,
                file_reference=sticker_set_item.document.file_reference,
            ).encode(),
            file_unique_id=FileUniqueId(
                file_unique_type=FileUniqueType.DOCUMENT, media_id=sticker_set_item.document.id
            ).encode(),
        )
