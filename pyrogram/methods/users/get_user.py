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
from pyrogram import types
from pyrogram.errors import PeerIdInvalid


class GetUser:
    async def get_user(self: pyrogram.Client, user_id: int | str) -> types.User:
        """Get information about one user, or fail saying which one is missing.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                A single user identifier (id or username).
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            :obj:`~pyrogram.types.User`: The user.

        Raises:
            PeerIdInvalid: In case *user_id* belongs to no user. The identifier is on the error's
                ``value``.

        Example:
            .. code-block:: python

                await app.get_user("me")
                await app.get_user(12345)
                await app.get_user("username")
        """

        user = await self.get_users(user_id)

        # `get_users()` answers `None` here for an identifier that belongs to no user: a channel,
        #  a chat, a deleted account, or a peer this account cannot see. That is the one thing a
        #  caller who named a single user cannot use, which is why this method exists beside it.
        if user is None:
            raise PeerIdInvalid(value=user_id)

        return user
