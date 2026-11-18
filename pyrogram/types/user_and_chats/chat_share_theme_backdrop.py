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

from typing import TYPE_CHECKING

from pyrogram import types

from ..object import Object

if TYPE_CHECKING:
    from pyrogram import raw


class ChatShareThemeBackdrop(Object):
    """This object describes a backdrop, which can be used as the background of a theme of the screen for sharing a link to a user or a chat.

    Parameters:
        id (``int``):
            Unique identifier of the backdrop.

        name (``str``):
            Name of the backdrop.

        colors (:obj:`~pyrogram.types.UniqueGiftBackdropColors`):
            Colors of the backdrop.
    """

    def __init__(self, *, id: int, name: str, colors: types.UniqueGiftBackdropColors) -> None:
        super().__init__()

        self.id = id
        self.name = name
        self.colors = colors

    @staticmethod
    def _parse(backdrop: raw.types.ShareThemeBackdropOption) -> ChatShareThemeBackdrop:
        return ChatShareThemeBackdrop(
            id=backdrop.backdrop_id,
            name=backdrop.name,
            colors=types.UniqueGiftBackdropColors(
                center_color=backdrop.center_color,
                edge_color=backdrop.edge_color,
                symbol_color=backdrop.pattern_color,
                text_color=backdrop.text_color,
            ),
        )
