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


class SetGameScore:
    async def set_game_score(
        self: pyrogram.Client,
        user_id: int | str,
        score: int,
        force: bool | None = None,
        disable_edit_message: bool | None = None,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
    ) -> types.Message | bool:
        """Set the score of the specified user in a game.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            score (``int``):
                New score, must be non-negative.

            force (``bool``, *optional*):
                Pass *True*, if the high score is allowed to decrease.
                This can be useful when fixing mistakes or banning cheaters.

            disable_edit_message (``bool``, *optional*):
                Pass *True*, if the game message should not be automatically edited to include the current scoreboard.

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
                Identifier of the sent message.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, if the message was sent by the bot, the edited
            message is returned, True otherwise.

        Example:
            .. code-block:: python

                # Set new score
                await app.set_game_score(chat_id=chat_id, message_id=message_id, user_id=user_id, score=1000)

                # Force set new score
                await app.set_game_score(chat_id=chat_id, message_id=message_id, user_id=user_id, score=25, force=True)
        """
        if inline_message_id is not None:
            unpacked = utils.unpack_inline_message_id(inline_message_id)
            dc_id = unpacked.dc_id

            session = await self.get_session(dc_id, is_media=True)

            r = await session.invoke(
                raw.functions.messages.SetInlineGameScore(
                    id=unpacked,
                    user_id=utils.get_input_user_or_channel(await self.resolve_peer(user_id)),
                    score=score,
                    edit_message=not disable_edit_message,
                    force=force,
                )
            )
        else:
            if chat_id is None or message_id is None:
                raise ValueError("chat_id and message_id are required")

            r = await self.invoke(
                raw.functions.messages.SetGameScore(
                    peer=await self.resolve_peer(chat_id),
                    id=message_id,
                    user_id=utils.get_input_user_or_channel(await self.resolve_peer(user_id)),
                    score=score,
                    edit_message=not disable_edit_message,
                    force=force,
                )
            )

        return next(iter(await utils.parse_messages(client=self, messages=r)), True)
