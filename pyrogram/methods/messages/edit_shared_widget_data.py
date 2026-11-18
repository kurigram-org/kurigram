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
from pyrogram import raw


class EditSharedWidgetData:
    async def edit_shared_widget_data(
        self: pyrogram.Client,
        widget_id: str,
        public_data: str,
        cache_time: int | None = None,
    ) -> bool:
        """Use this method to edit public data of a shared widget created by the bot.

        A shared widget can be edited at most once per second.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            widget_id (``str``):
                Unique identifier of the shared widget.

            public_data (``str``):
                New public data of the widget, 0-1024 bytes.
                Pass an empty string to remove the public data.

            cache_time (``int``, *optional*):
                The maximum amount of time in seconds that the public data of the widget may be cached client-side,
                5-3600.
                If omitted, then the current value is kept, which is 30 by default.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.messages.EditWidgetData(
                widget_id=int(widget_id),
                public_data=public_data,
                cache_time=cache_time,
            )
        )
