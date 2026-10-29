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

from typing import TYPE_CHECKING, Final

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.errors import PeerIdInvalid
from pyrogram.methods.advanced.resolve_peer import ResolvePeer

if TYPE_CHECKING:
    import re


class EmptyStorage:
    """A session that has met no peer at all."""

    async def get_peer_by_id(self, peer_id: int) -> raw.base.InputPeer:
        raise KeyError(peer_id)


class Answerer(ResolvePeer):
    """A client whose session has met nobody and whose server vouches for nobody either."""

    CHANNEL_MESSAGE_LINK_RE: Final[re.Pattern[str]] = pyrogram.Client.CHANNEL_MESSAGE_LINK_RE
    is_connected: bool = True
    storage: EmptyStorage = EmptyStorage()

    async def invoke(
        self,
        query: raw.core.TLObject,
    ) -> list[raw.base.User] | raw.types.messages.Chats:
        if isinstance(query, raw.functions.users.GetUsers):
            return [raw.types.UserEmpty(id=42)]

        return raw.types.messages.Chats(chats=[])

    async def fetch_peers(self, peers: list[raw.base.User]) -> bool:
        return False


@pytest.mark.parametrize(
    "peer_id",
    [
        pytest.param(42, id="user"),
        pytest.param(-42, id="basic-group"),
        pytest.param(-1000000000042, id="channel"),
        pytest.param("https://t.me/c/42/1", id="channel-link"),
        pytest.param("@", id="no-username"),
    ],
)
@pytest.mark.asyncio
async def test_an_identifier_nobody_vouches_for_is_named_on_the_error(peer_id: int | str) -> None:
    # `get_user()`, `get_chat()` and `get_chats()` all resolve before they ask, so this is where
    #  an identifier the session never met fails for them. Raised bare, the error left `value`
    #  as `None` while their docs promise the identifier there.
    with pytest.raises(PeerIdInvalid) as raised:
        await Answerer().resolve_peer(peer_id)

    assert raised.value.value == peer_id


@pytest.mark.asyncio
async def test_an_identifier_of_no_known_type_is_named_on_the_error() -> None:
    # Neither an id nor a username, so nothing can resolve it, and the caller still has to be
    #  told which argument it was.
    with pytest.raises(PeerIdInvalid) as raised:
        await Answerer().resolve_peer(b"42")

    assert raised.value.value == b"42"
