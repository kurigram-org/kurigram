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
from pyrogram import raw, types
from pyrogram.parser.rich_message import RichMessageSerializer

from ..object import Object


class RichMessage(Object):
    """Rich formatted message.

    Parameters:
        blocks (List of :obj:`pyrogram.types.RichBlock`):
            Content of the message.

        is_rtl (``bool``, *optional*):
            True, if the rich message must be shown right-to-left.

        is_partial (``bool``, *optional*):
            True, if the rich message is one part of a larger one.
    """

    def __init__(
        self,
        *,
        blocks: list[types.RichBlock],
        is_rtl: bool | None = None,
        is_partial: bool | None = None,
    ) -> None:
        super().__init__()

        self.blocks = blocks
        self.is_rtl = is_rtl
        self.is_partial = is_partial

    @property
    def html(self) -> str:
        """Telegram rich HTML with reusable file IDs embedded in media links.

        Unsupported content emits UnsupportedRichContentWarning and is skipped.
        """
        return RichMessageSerializer().render(self, html=True)

    @property
    def markdown(self) -> str:
        """Telegram rich Markdown, with HTML for structures Markdown cannot preserve.

        This differs from Message.text.markdown. Media links embed reusable file IDs
        which InputRichMessage resolves automatically when sending.
        """
        return RichMessageSerializer().render(self, html=False)

    def to_input(self, format: str = "html") -> types.InputRichMessage:
        """Convert to a sendable rich message, retaining media and RTL direction.

        Parameters:
            format (``str``): Either "html" (default) or "markdown".

        Unsupported content warns and is skipped. An entirely unsupported tree
        produces empty content, which cannot be sent as a rich message.
        """
        if format not in ("html", "markdown"):
            raise ValueError('Rich message format must be "html" or "markdown"')

        serializer = RichMessageSerializer()
        content = serializer.render(self, html=format == "html")

        return types.InputRichMessage(**{format: content}, is_rtl=self.is_rtl)

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        rich_message: raw.types.RichMessage,
        users: dict[int, raw.base.User] | None = None,
        chats: dict[int, raw.base.Chat] | None = None,
    ) -> RichMessage:
        users = users or {}
        chats = chats or {}

        if isinstance(rich_message, raw.types.RichMessage):
            photos = {photo.id: photo for photo in rich_message.photos}
            documents = {document.id: document for document in rich_message.documents}

            return RichMessage(
                blocks=types.List(
                    [
                        await types.RichBlock._parse(
                            client,
                            block,
                            photos,
                            documents,
                            users,
                            chats,
                        )
                        for block in rich_message.blocks
                    ]
                ),
                is_rtl=rich_message.rtl,
                is_partial=rich_message.part,
            )
