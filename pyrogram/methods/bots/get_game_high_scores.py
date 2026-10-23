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
from pyrogram import raw, types, utils


class GetGameHighScores:
    async def get_game_high_scores(
        self: pyrogram.Client,
        user_id: int | str,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
    ) -> list[types.GameHighScore]:
        """Get data for high score tables.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            chat_id (``int`` | ``str``, *optional*):
                Required if *inline_message_id* is not specified.
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``, *optional*):
                Required if *inline_message_id* is not specified.
                Identifier of the sent message.

            inline_message_id (``str``, *optional*):
                Required if *chat_id* and *message_id* are not specified.
                Identifier of the inline message.

        Returns:
            List of :obj:`~pyrogram.types.GameHighScore`: On success.

        Example:
            .. code-block:: python

                scores = await app.get_game_high_scores(user_id, chat_id, message_id)
                print(scores)

                # A game sent via inline mode
                scores = await app.get_game_high_scores(user_id, inline_message_id=inline_message_id)
        """
        if inline_message_id is not None:
            unpacked = utils.unpack_inline_message_id(inline_message_id)

            session = await self.get_session(unpacked.dc_id, is_media=True)

            high_scores = await session.invoke(
                raw.functions.messages.GetInlineGameHighScores(
                    id=unpacked,
                    user_id=await self.resolve_peer(user_id),
                ),
                sleep_threshold=self.sleep_threshold,
            )
        else:
            if chat_id is None or message_id is None:
                raise ValueError("chat_id and message_id are required")

            high_scores = await self.invoke(
                raw.functions.messages.GetGameHighScores(
                    peer=await self.resolve_peer(chat_id),
                    id=message_id,
                    user_id=await self.resolve_peer(user_id),
                )
            )

        return types.List(
            [
                await types.GameHighScore._parse(self, score, high_scores.users)
                for score in high_scores.scores
            ]
        )
