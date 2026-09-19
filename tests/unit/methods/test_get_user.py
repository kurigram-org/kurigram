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

import pytest

from pyrogram import types
from pyrogram.errors import PeerIdInvalid
from pyrogram.methods.users.get_user import GetUser


class Answerer(GetUser):
    """A client whose `get_users()` answers with a fixed result, whatever it is asked."""

    def __init__(self, answer: types.User | None) -> None:
        self.answer = answer

    async def get_users(self, user_ids: int | str) -> types.User | None:
        return self.answer


@pytest.mark.asyncio
async def test_an_identifier_that_belongs_to_no_user_raises() -> None:
    # `get_users()` keeps its `None` for a channel, a chat, a deleted account or a peer this
    #  account cannot see. `get_user()` exists to turn exactly that into an error at the call
    #  site, so the identifier is named where the caller can still act on it.
    with pytest.raises(PeerIdInvalid) as raised:
        await Answerer(None).get_user("a_channel_username")

    assert raised.value.value == "a_channel_username"


@pytest.mark.asyncio
async def test_a_user_that_exists_is_handed_straight_back() -> None:
    user = types.User(id=42)

    assert await Answerer(user).get_user(42) is user
