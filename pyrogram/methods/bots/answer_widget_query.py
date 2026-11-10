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


class AnswerWidgetQuery:
    async def answer_widget_query(
        self: pyrogram.Client,
        widget_query_id: str,
        data: str | None = None,
    ) -> bool:
        """Use this method to send an answer to a query from a widget.

        The query must be answered within 15 seconds. The answer is received only by the widget that sent the query
        and doesn't change data of the widget. Use :meth:`~pyrogram.Client.edit_message_widget_data` or
        :meth:`~pyrogram.Client.edit_shared_widget_data` to change it.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            widget_query_id (``str``):
                Unique identifier for the query to be answered.

            data (``str``, *optional*):
                Data to be returned to the widget, 0-1024 bytes.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.messages.SetBotWidgetQueryAnswer(
                query_id=int(widget_query_id),
                result=data,
            )
        )
