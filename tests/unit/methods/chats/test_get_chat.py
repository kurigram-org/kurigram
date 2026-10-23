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

import re
from typing import Final

import pytest

from pyrogram import raw
from pyrogram.methods.chats.get_chat import GetChat

_CHANNEL_ID: Final = 42


class FakeClient(GetChat):
    """A client whose channels.GetChannels answers with a sliced result."""

    INVITE_LINK_RE = re.compile(
        r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:joinchat/|\+))([\w-]+)$"
    )

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerChannel(channel_id=_CHANNEL_ID, access_hash=0)

    async def invoke(
        self, query: raw.functions.channels.GetChannels
    ) -> raw.types.messages.ChatsSlice:
        return raw.types.messages.ChatsSlice(
            count=1,
            chats=[
                raw.types.Channel(
                    id=_CHANNEL_ID,
                    title="Channel 42",
                    photo=raw.types.ChatPhotoEmpty(),
                    date=0,
                    usernames=[],
                    restriction_reason=[],
                )
            ],
        )


@pytest.mark.asyncio
async def test_a_sliced_channel_result_is_resolved() -> None:
    # GetChannels/GetChats can answer with either messages.Chats or
    #  messages.ChatsSlice: the code only special-cased the former and fell back to
    #  subscripting the raw response itself, which crashed with TypeError for
    #  ChatsSlice (it isn't a list; the chats live under its `.chats` attribute,
    #  same as on messages.Chats).
    chat = await FakeClient().get_chat(-_CHANNEL_ID, force_full=False)

    assert chat.id == -1000000000000 - _CHANNEL_ID
    assert chat.title == "Channel 42"


class EmptyPeerClient(GetChat):
    """A client whose lookups answer with the empty constructor of the peer."""

    INVITE_LINK_RE: Final[re.Pattern[str]] = FakeClient.INVITE_LINK_RE

    def __init__(self, peer: raw.base.InputPeer) -> None:
        self._peer = peer

    async def resolve_peer(self, peer_id: int | str) -> raw.base.InputPeer:
        return self._peer

    async def invoke(
        self,
        query: raw.core.TLObject,
    ) -> list[raw.base.User] | raw.types.messages.Chats:
        if isinstance(query, raw.functions.users.GetUsers):
            return [raw.types.UserEmpty(id=_CHANNEL_ID)]

        return raw.types.messages.Chats(chats=[raw.types.ChatEmpty(id=_CHANNEL_ID)])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "peer",
    [
        raw.types.InputPeerUser(
            user_id=_CHANNEL_ID,
            access_hash=0,
        ),
        raw.types.InputPeerChat(chat_id=_CHANNEL_ID),
    ],
    ids=["user", "group"],
)
async def test_an_empty_peer_returns_none(peer: raw.base.InputPeer) -> None:
    # The docstring promises `None` when the server answers with an empty
    #  peer; the parser raises `EmptyObjectError` on one instead.
    assert await EmptyPeerClient(peer).get_chat(_CHANNEL_ID, force_full=False) is None
