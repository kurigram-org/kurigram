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

import zlib
from typing import TYPE_CHECKING

from ..object import Object

if TYPE_CHECKING:
    from pyrogram import raw


class Widget(Object):
    """This object describes an `HTML widget <https://core.telegram.org/bots/widgets>`_.

    Parameters:
        id (``str``, *optional*):
            Unique identifier of the shared widget, which can be used to send the widget again using the method :meth:`~pyrogram.Client.send_shared_widget` to send the widget again.
            Omitted if the widget isn't shared.

        width (``int``, *optional*):
            Width of the widget in logical pixels.
            Omitted if the widget must occupy the whole width of the message bubble.

        height (``int``, *optional*):
            Height of the widget in logical pixels.
            Omitted if the height of the widget isn't fixed.

        html (``str``):
            HTML code of the widget.

        public_data (``str``, *optional*):
            Public data of the widget, which is available wherever the widget is shown.
            All messages with a shared widget have the same public data.

        chat_data (``str``, *optional*):
            Data of the widget, which is specific to the message.

        raw (:obj:`~pyrogram.raw.types.MessageMediaWidget`, *optional*):
            The raw widget object, as received from the Telegram API.
    """

    def __init__(
        self,
        *,
        id: str | None = None,
        width: int | None = None,
        height: int | None = None,
        html: str,
        public_data: str | None = None,
        chat_data: str | None = None,
        raw: raw.types.MessageMediaWidget | None = None,
    ) -> None:
        super().__init__()

        self.id = id
        self.width = width
        self.height = height
        self.html = html
        self.public_data = public_data
        self.chat_data = chat_data
        self.raw = raw

    @staticmethod
    def _parse(widget: raw.types.MessageMediaWidget) -> Widget | None:
        try:
            # Adding 32 lets zlib detect either a zlib or a gzip header.
            html = zlib.decompress(widget.payload, wbits=zlib.MAX_WBITS | 32).decode("utf-8")
        except (zlib.error, UnicodeDecodeError):
            return None

        if not html:
            return None

        return Widget(
            html=html,
            id=str(widget.widget_id) if widget.widget_id else None,
            width=widget.width or None,
            height=widget.height or None,
            public_data=widget.public_data,
            chat_data=widget.chat_data,
            raw=widget,
        )
