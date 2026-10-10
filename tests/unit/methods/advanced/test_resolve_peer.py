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

"""`resolve_peer` for a `min` peer: through the messages it was seen in.

The client is real, with an in-memory storage, so what `fetch_peers` stores and what
`resolve_peer` reads back are the library's own. Only `invoke` is replaced: it records each
query and answers from the test, then stores the answer's peers the way the real one does.
"""

from __future__ import annotations as _annotations

from typing import TYPE_CHECKING, Any, Final

import pytest

from pyrogram import Client, errors, raw, utils
from pyrogram.utils.cache import Sighting

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

_GROUP: Final[int] = 1234567  # The supergroup the sightings are in, fully known.
_OTHER_GROUP: Final[int] = 1234568
_UNKNOWN_GROUP: Final[int] = 1234569
_USER: Final[int] = 777001
_CHANNEL: Final[int] = 7654321

_GROUP_ID: Final[int] = utils.get_channel_id(_GROUP)
_OTHER_GROUP_ID: Final[int] = utils.get_channel_id(_OTHER_GROUP)
_UNKNOWN_GROUP_ID: Final[int] = utils.get_channel_id(_UNKNOWN_GROUP)
_CHANNEL_ID: Final[int] = utils.get_channel_id(_CHANNEL)


def a_user(*, is_min: bool, user_id: int = _USER) -> raw.types.User:
    return raw.types.User(id=user_id, min=is_min, access_hash=999, first_name="u", usernames=[])


def a_channel(
    channel_id: int, *, is_min: bool = False, megagroup: bool = False
) -> raw.types.Channel:
    return raw.types.Channel(
        id=channel_id,
        title="c",
        photo=raw.types.ChatPhotoEmpty(),
        date=0,
        min=is_min,
        megagroup=megagroup,
        broadcast=not megagroup,
        access_hash=555,
        usernames=[],
        restriction_reason=[],
    )


class Server:
    """Stands in for `Client.invoke`: records each query and answers with `respond(query)`."""

    def __init__(self, client: Client) -> None:
        self.client = client
        self.queries: list[raw.core.TLObject] = []
        self.respond: Callable[[raw.core.TLObject], Any] = lambda query: pytest.fail(
            f"unexpected request {query!r}"
        )

    async def __call__(self, query: raw.core.TLObject, *args: Any, **kwargs: Any) -> Any:
        self.queries.append(query)
        answer = self.respond(query)

        if isinstance(answer, Exception):
            raise answer

        # What the real `invoke` does with every answer.
        await self.client.fetch_peers(getattr(answer, "users", []))
        await self.client.fetch_peers(getattr(answer, "chats", []))

        return answer


@pytest.fixture
async def client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[Client]:
    client = Client("resolve_peer_probe", api_id=1, api_hash="0" * 32, in_memory=True)
    await client.storage.open()
    client.is_connected = True

    await client.fetch_peers(
        [a_channel(_GROUP, megagroup=True), a_channel(_OTHER_GROUP, megagroup=True)]
    )
    monkeypatch.setattr(client, "invoke", Server(client))

    yield client

    await client.storage.close()


def server_of(client: Client) -> Server:
    server = client.invoke
    assert isinstance(server, Server)

    return server


async def test_a_stored_peer_needs_no_sighting_and_no_request(client: Client) -> None:
    await client.fetch_peers([a_user(is_min=False)])
    await client.min_peer_cache.add([_USER], _GROUP_ID, 42)

    peer = await client.resolve_peer(_USER)

    assert isinstance(peer, raw.types.InputPeerUser)
    assert server_of(client).queries == []


async def test_a_min_user_is_asked_for_through_the_message_it_was_seen_in(client: Client) -> None:
    await client.min_peer_cache.add([_USER], _GROUP_ID, 42)
    server_of(client).respond = lambda query: [a_user(is_min=True)]

    peer = await client.resolve_peer(_USER)

    (query,) = server_of(client).queries
    assert isinstance(query, raw.functions.users.GetUsers)
    (input_user,) = query.id
    assert isinstance(input_user, raw.types.InputUserFromMessage)
    assert isinstance(input_user.peer, raw.types.InputPeerChannel)
    assert input_user.peer.channel_id == _GROUP
    assert (input_user.msg_id, input_user.user_id) == (42, _USER)

    # Still `min` in the answer, so the sighting is what addresses it.
    assert isinstance(peer, raw.types.InputPeerUserFromMessage)
    assert (peer.peer.channel_id, peer.msg_id, peer.user_id) == (_GROUP, 42, _USER)


async def test_a_full_answer_is_stored_and_used_from_then_on(client: Client) -> None:
    await client.min_peer_cache.add([_USER], _GROUP_ID, 42)
    server_of(client).respond = lambda query: [a_user(is_min=False)]

    peer = await client.resolve_peer(_USER)
    again = await client.resolve_peer(_USER)

    assert isinstance(peer, raw.types.InputPeerUser)
    assert peer.access_hash == 999
    assert isinstance(again, raw.types.InputPeerUser)
    assert len(server_of(client).queries) == 1


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        (a_channel(_CHANNEL, is_min=True), raw.types.InputPeerChannelFromMessage),
        (a_channel(_CHANNEL), raw.types.InputPeerChannel),
        (
            raw.types.ChannelForbidden(id=_CHANNEL, access_hash=555, title="c", broadcast=True),
            raw.types.InputPeerChannel,
        ),
    ],
)
async def test_a_min_channel_is_asked_for_through_the_message_it_was_seen_in(
    client: Client, answer: raw.base.Chat, expected: type
) -> None:
    await client.min_peer_cache.add([_CHANNEL_ID], _GROUP_ID, 42)
    server_of(client).respond = lambda query: raw.types.messages.Chats(chats=[answer])

    peer = await client.resolve_peer(_CHANNEL_ID)

    (query,) = server_of(client).queries
    assert isinstance(query, raw.functions.channels.GetChannels)
    (input_channel,) = query.id
    assert isinstance(input_channel, raw.types.InputChannelFromMessage)
    assert (input_channel.msg_id, input_channel.channel_id) == (42, _CHANNEL)
    assert type(peer) is expected


async def test_the_newest_sighting_is_tried_first(client: Client) -> None:
    await client.min_peer_cache.add([_USER], _GROUP_ID, 1)
    await client.min_peer_cache.add([_USER], _OTHER_GROUP_ID, 2)
    server_of(client).respond = lambda query: [a_user(is_min=True)]

    peer = await client.resolve_peer(_USER)

    assert peer.peer.channel_id == _OTHER_GROUP
    assert len(server_of(client).queries) == 1


@pytest.mark.parametrize(
    "error",
    [
        errors.ChannelInvalid,
        errors.ChannelMonoforumUnsupported,
        errors.ChannelPrivate,
        errors.MsgIdInvalid,
        errors.PeerIdInvalid,
        errors.UserBannedInChannel,
    ],
)
async def test_a_stale_sighting_is_forgotten_and_the_next_one_tried(
    client: Client, error: type[errors.RPCError]
) -> None:
    await client.min_peer_cache.add([_USER], _GROUP_ID, 1)
    await client.min_peer_cache.add([_USER], _OTHER_GROUP_ID, 2)

    def respond(query: raw.functions.users.GetUsers) -> object:
        return error() if query.id[0].peer.channel_id == _OTHER_GROUP else [a_user(is_min=True)]

    server_of(client).respond = respond

    peer = await client.resolve_peer(_USER)

    assert peer.peer.channel_id == _GROUP
    assert await client.min_peer_cache.get(_USER) == [Sighting(_GROUP_ID, 1)]


@pytest.mark.parametrize(
    "answer",
    [
        [],
        # A deleted account.
        [raw.types.UserEmpty(id=_USER)],
        [a_user(is_min=True, user_id=_USER + 1)],
    ],
)
async def test_an_answer_without_the_user_counts_as_stale(
    client: Client, answer: list[raw.base.User]
) -> None:
    await client.min_peer_cache.add([_USER], _GROUP_ID, 1)

    def respond(query: raw.functions.users.GetUsers) -> object:
        # The `access_hash=0` request that follows when no sighting works.
        if isinstance(query.id[0], raw.types.InputUser):
            return []

        return answer

    server_of(client).respond = respond

    with pytest.raises(errors.PeerIdInvalid):
        await client.resolve_peer(_USER)

    assert _USER not in client.min_peer_cache


async def test_an_answer_without_the_channel_counts_as_stale(client: Client) -> None:
    await client.min_peer_cache.add([_CHANNEL_ID], _GROUP_ID, 1)
    server_of(client).respond = lambda query: raw.types.messages.Chats(chats=[])

    with pytest.raises(errors.PeerIdInvalid):
        await client.resolve_peer(_CHANNEL_ID)

    assert _CHANNEL_ID not in client.min_peer_cache


async def test_a_sighting_in_a_chat_not_in_storage_is_forgotten_without_a_request(
    client: Client,
) -> None:
    # No `InputPeer` to put in `InputUserFromMessage.peer`. TDLib never records one.
    await client.min_peer_cache.add([_USER], _UNKNOWN_GROUP_ID, 1)
    await client.min_peer_cache.add([_USER], _GROUP_ID, 2)
    await client.min_peer_cache.add([_USER], _UNKNOWN_GROUP_ID, 3)
    server_of(client).respond = lambda query: [a_user(is_min=True)]

    peer = await client.resolve_peer(_USER)

    assert peer.peer.channel_id == _GROUP
    assert len(server_of(client).queries) == 1
    assert await client.min_peer_cache.get(_USER) == [Sighting(_GROUP_ID, 2)]


async def test_an_error_unrelated_to_the_sighting_is_raised_and_the_sighting_kept(
    client: Client,
) -> None:
    await client.min_peer_cache.add([_USER], _GROUP_ID, 1)
    server_of(client).respond = lambda query: errors.FloodWait(5)

    with pytest.raises(errors.FloodWait):
        await client.resolve_peer(_USER)

    assert await client.min_peer_cache.get(_USER) == [Sighting(_GROUP_ID, 1)]


async def test_without_a_sighting_the_access_hash_zero_request_still_runs(client: Client) -> None:
    server_of(client).respond = lambda query: [a_user(is_min=False)]

    peer = await client.resolve_peer(_USER)

    (query,) = server_of(client).queries
    assert isinstance(query.id[0], raw.types.InputUser)
    assert query.id[0].access_hash == 0
    assert isinstance(peer, raw.types.InputPeerUser)


async def test_a_basic_group_never_looks_at_the_sightings(client: Client) -> None:
    # `*FromMessage` exists for users and channels only.
    await client.min_peer_cache.add([-42], _GROUP_ID, 1)

    def respond(query: raw.core.TLObject) -> object:
        assert isinstance(query, raw.functions.messages.GetChats)

        return raw.types.messages.Chats(
            chats=[
                raw.types.Chat(
                    id=42,
                    title="g",
                    photo=raw.types.ChatPhotoEmpty(),
                    participants_count=1,
                    date=0,
                    version=1,
                )
            ]
        )

    server_of(client).respond = respond

    peer = await client.resolve_peer(-42)

    assert isinstance(peer, raw.types.InputPeerChat)
    assert len(server_of(client).queries) == 1
