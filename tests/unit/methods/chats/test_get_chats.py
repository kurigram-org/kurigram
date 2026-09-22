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

from pyrogram import raw
from pyrogram.methods.chats.get_chats import GetChats


class Answerer(GetChats):
    """A client that answers each of the three peer calls out of one pool of raw chats."""

    def __init__(
        self,
        peers: dict[int | str, raw.base.InputPeer],
        raw_chats: list[raw.base.Chat | raw.base.User],
    ) -> None:
        self.peers = peers
        self.raw_chats = raw_chats
        self.queries: list[raw.core.TLObject] = []

    async def resolve_peer(self, peer_id: int | str) -> raw.base.InputPeer:
        return self.peers[peer_id]

    async def invoke(
        self,
        query: raw.core.TLObject,
    ) -> raw.types.messages.Chats | list[raw.base.User]:
        self.queries.append(query)

        if isinstance(query, raw.functions.channels.GetChannels):
            return raw.types.messages.Chats(chats=_only(self.raw_chats, wanted=raw.types.Channel))

        if isinstance(query, raw.functions.messages.GetChats):
            return raw.types.messages.Chats(
                chats=_only(self.raw_chats, wanted=(raw.types.Chat, raw.types.ChatEmpty))
            )

        return _only(self.raw_chats, wanted=(raw.types.User, raw.types.UserEmpty))


def _only(
    raw_chats: list[raw.base.Chat | raw.base.User],
    *,
    wanted: type | tuple[type, ...],
) -> list[raw.base.Chat | raw.base.User]:
    return [raw_chat for raw_chat in raw_chats if isinstance(raw_chat, wanted)]


def a_user_peer(user_id: int) -> raw.types.InputPeerUser:
    return raw.types.InputPeerUser(
        user_id=user_id,
        access_hash=0,
    )


def a_channel_peer(channel_id: int) -> raw.types.InputPeerChannel:
    return raw.types.InputPeerChannel(
        channel_id=channel_id,
        access_hash=0,
    )


def a_channel(channel_id: int) -> raw.types.Channel:
    return raw.types.Channel(
        id=channel_id,
        title=f"Channel {channel_id}",
        photo=raw.types.ChatPhotoEmpty(),
        date=0,
        usernames=[],
        restriction_reason=[],
    )


def a_group(group_id: int) -> raw.types.Chat:
    return raw.types.Chat(
        id=group_id,
        title=f"Group {group_id}",
        photo=None,
        participants_count=2,
        date=0,
        version=1,
    )


def a_user(user_id: int, *, is_self: bool | None = None) -> raw.types.User:
    # `usernames` and `restriction_reason` are `flags.N?Vector<...>`, and the generated `read()`
    #  gives an absent vector back as `[]`. The parsers iterate both without guarding, so a
    #  hand-built `raw.types.User` has to spell out what the wire implies.
    return raw.types.User(
        id=user_id,
        first_name=f"User {user_id}",
        is_self=is_self,
        usernames=[],
        restriction_reason=[],
    )


@pytest.mark.asyncio
async def test_a_single_identifier_that_names_no_chat_gives_nothing_back() -> None:
    peers = {-42: raw.types.InputPeerChat(chat_id=42)}

    assert await Answerer(peers, []).get_chats(-42) is None


@pytest.mark.asyncio
async def test_a_single_identifier_gives_its_chat_back() -> None:
    peers = {-42: raw.types.InputPeerChat(chat_id=42)}

    chat = await Answerer(peers, [a_group(42)]).get_chats(-42)

    assert chat.id == -42
    assert chat.title == "Group 42"


@pytest.mark.asyncio
async def test_a_list_comes_back_in_the_order_it_was_asked_for() -> None:
    # The three kinds of peer are three separate calls, so the answers arrive grouped by kind
    #  rather than in the order asked. Handing that grouping back would silently reorder a list
    #  the caller is about to zip against its own input.
    peers = {
        7: a_user_peer(7),
        -42: raw.types.InputPeerChat(chat_id=42),
        -1000000000099: a_channel_peer(99),
    }

    chats = await Answerer(peers, [a_channel(99), a_user(7), a_group(42)]).get_chats(
        [7, -42, -1000000000099]
    )

    assert [chat.id for chat in chats] == [7, -42, -1000000000099]


@pytest.mark.asyncio
async def test_a_list_leaves_out_a_chat_this_account_can_no_longer_see() -> None:
    # `chatEmpty` is what the server answers for a chat the account has lost access to. A list
    #  holding the `None` it parses to holds a hole nobody can iterate past.
    peers = {
        -42: raw.types.InputPeerChat(chat_id=42),
        -43: raw.types.InputPeerChat(chat_id=43),
    }

    chats = await Answerer(peers, [a_group(42), raw.types.ChatEmpty(id=43)]).get_chats([-42, -43])

    assert [chat.id for chat in chats] == [-42]


@pytest.mark.asyncio
async def test_saved_messages_is_matched_through_the_self_flag() -> None:
    # `inputPeerSelf` carries no identifier, so the answer is the only thing that names the
    #  account's own chat. Without reading the `self` flag off it, "me" came back missing.
    peers = {"me": raw.types.InputPeerSelf()}

    chat = await Answerer(peers, [a_user(7, is_self=True)]).get_chats("me")

    assert chat.id == 7


@pytest.mark.asyncio
async def test_one_call_is_made_per_kind_of_peer_however_many_identifiers() -> None:
    peers = {
        7: a_user_peer(7),
        8: a_user_peer(8),
        -42: raw.types.InputPeerChat(chat_id=42),
        -43: raw.types.InputPeerChat(chat_id=43),
        -1000000000099: a_channel_peer(99),
    }
    answerer = Answerer(peers, [])

    await answerer.get_chats(list(peers))

    assert len(answerer.queries) == 3
