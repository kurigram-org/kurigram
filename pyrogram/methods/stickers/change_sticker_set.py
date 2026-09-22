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
from pyrogram import raw


class ChangeStickerSet:
    async def change_sticker_set(
        self: pyrogram.Client,
        name: str,
        is_installed: bool,
        is_archived: bool,
    ) -> bool:
        """Installs/uninstalls or activates/archives a sticker set.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            name (``str``):
                Name of the sticker set.

            is_installed (``bool``):
                The new value of is_installed.

            is_archived (``bool``):
                The new value of is_archived.

        Returns:
            ``bool``: True, on success.
        """
        if is_installed:
            r = await self.invoke(
                raw.functions.messages.InstallStickerSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=name),
                    archived=is_archived,
                )
            )

            return bool(r)

        r = await self.invoke(
            raw.functions.messages.UninstallStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=name)
            )
        )

        return bool(r)
