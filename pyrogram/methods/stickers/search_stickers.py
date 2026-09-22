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

from collections.abc import AsyncGenerator

import pyrogram
from pyrogram import enums, raw, types


class SearchStickers:
    async def search_stickers(
        self: pyrogram.Client,
        sticker_type: enums.StickerType,
        emojis: list[str],
        query: str = "",
        input_languages_codes: list[str] | None = None,
        offset: int = 0,
        limit: int = 0,
    ) -> AsyncGenerator[types.Sticker, None]:
        """Searches for stickers from public sticker sets that correspond to any of the given emoji.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            sticker_type (:obj:`~pyrogram.enums.StickerType`):
                Type of the stickers to return.

            emojis (List of ``str``):
                List of emojis to search for.

            query (``str``, *optional*):
                Query to search for.
                May be empty to search for emoji only.

            input_languages_codes (List of ``str``, *optional*):
                List of possible IETF language tags of the user's input language.

            offset (``int``, *optional*):
                The offset from which to return the stickers.

            limit (``int``, *optional*):
                Limits the number of stickers to be retrieved.
                By default, no limit is applied and all stickers are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Sticker` objects.
        """
        current = 0
        total = abs(limit) or (1 << 31) - 1
        limit = min(100, total)

        while True:
            r = await self.invoke(
                raw.functions.messages.SearchStickers(
                    q=query,
                    emoticon="".join(emojis),
                    lang_code=input_languages_codes or [],
                    offset=offset,
                    limit=limit,
                    hash=0,
                    emojis=sticker_type == enums.StickerType.CUSTOM_EMOJI,
                )
            )

            stickers = [
                await types.Sticker._parse(
                    client=self,
                    sticker=sticker,
                    document_attributes={type(i): i for i in sticker.attributes},
                )
                for sticker in r.stickers
            ]

            if not stickers:
                return

            for sticker in stickers:
                yield sticker

                current += 1

                if current >= total:
                    return

            offset = r.next_offset

            if not offset:
                return
