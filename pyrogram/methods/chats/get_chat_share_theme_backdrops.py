#  Kurigram - Telegram MTProto API Client Library for Python
#
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2024-present KurimuzonAkuma <https://github.com/KurimuzonAkuma>
#
#  This file is part of Kurigram.
#
#  Kurigram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Kurigram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Kurigram. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations

import pyrogram
from pyrogram import raw, types, utils


class GetChatShareThemeBackdrops:
    async def get_chat_share_theme_backdrops(
        self: pyrogram.Client,
    ) -> list[types.ChatShareThemeBackdrop]:
        """Use this method to get the list of backdrops, which can be used as the background of a theme of the screen for sharing a link to a user or a chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Returns:
            List of :obj:`~pyrogram.types.ChatShareThemeBackdrop`: On success, a list of backdrops is returned.
        """
        r = await self.invoke(raw.functions.messages.GetShareThemeBackdrops(hash=0))

        backdrops = types.List(
            [
                types.ChatShareThemeBackdrop._parse(backdrop)
                for backdrop in getattr(r, "backdrops", [])
            ]
        )

        return utils.require_parsed(backdrops)
