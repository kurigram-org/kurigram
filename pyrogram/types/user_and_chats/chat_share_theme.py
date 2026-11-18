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
from pyrogram import raw, types

from ..object import Object


class ChatShareTheme(Object):
    """This object describes the theme of the screen for sharing a link to a user or a chat.

    It can be one of:

    - :obj:`~pyrogram.types.ChatShareThemeEmoji`
    - :obj:`~pyrogram.types.ChatShareThemeUniqueGift`
    """

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        theme: raw.base.ShareTheme | None,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> ChatShareTheme | None:
        if isinstance(theme, raw.types.ShareThemeEmojiBackdrop):
            emojis = types.List()

            for reaction in theme.emojis or []:
                emoji = types.EmojiType._parse(reaction)
                if emoji is not None:
                    emojis.append(emoji)

            return ChatShareThemeEmoji(
                emojis=emojis,
                background_backdrop_id=theme.backdrop_id,
            )
        if isinstance(theme, raw.types.ShareThemeGift):
            return ChatShareThemeUniqueGift(
                gift=await types.Gift._parse(client, theme.stargift, users=users, chats=chats)
            )
        return None


class ChatShareThemeEmoji(ChatShareTheme):
    """The theme with emoji placed on a background.

    Parameters:
        emojis (List of :obj:`~pyrogram.types.EmojiType`):
            The emoji, 0-6 regular or custom emoji.

        background_backdrop_id (``int``, *optional*):
            Identifier of the backdrop used as the background. Omitted if the default background is used.
            Use :meth:`~pyrogram.Client.get_chat_share_theme_backdrops` to get details about the backdrop.
    """

    def __init__(
        self, *, emojis: list[types.EmojiType], background_backdrop_id: int | None = None
    ) -> None:
        super().__init__()

        self.emojis = emojis
        self.background_backdrop_id = background_backdrop_id


class ChatShareThemeUniqueGift(ChatShareTheme):
    """The theme based on a unique gift owned by the user or the chat.

    Parameters:
        gift (:obj:`~pyrogram.types.Gift`):
            The gift.
    """

    def __init__(self, *, gift: types.Gift) -> None:
        super().__init__()

        self.gift = gift
