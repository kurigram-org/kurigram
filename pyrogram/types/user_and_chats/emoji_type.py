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

from pyrogram import raw

from ..object import Object


class EmojiType(Object):
    """This object describes an emoji.

    It can be one of:

    - :obj:`~pyrogram.types.EmojiTypeEmoji`
    - :obj:`~pyrogram.types.EmojiTypeCustomEmoji`
    """

    @staticmethod
    def _parse(emoji: raw.base.Reaction) -> EmojiType | None:
        if isinstance(emoji, raw.types.ReactionEmoji):
            return EmojiTypeEmoji(emoji=emoji.emoticon)
        if isinstance(emoji, raw.types.ReactionCustomEmoji):
            return EmojiTypeCustomEmoji(custom_emoji_id=str(emoji.document_id))
        return None


class EmojiTypeEmoji(EmojiType):
    """A regular emoji.

    Parameters:
        emoji (``str``):
            The emoji.
    """

    def __init__(self, *, emoji: str) -> None:
        super().__init__()

        self.emoji = emoji


class EmojiTypeCustomEmoji(EmojiType):
    """A custom emoji.

    Parameters:
        custom_emoji_id (``str``):
            Identifier of the custom emoji.
            Use :meth:`~pyrogram.Client.get_custom_emoji_stickers` to get full information about the sticker.
    """

    def __init__(self, *, custom_emoji_id: str) -> None:
        super().__init__()

        self.custom_emoji_id = custom_emoji_id
