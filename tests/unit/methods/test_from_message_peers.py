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

"""Methods given a `*FromMessage` peer, the form a `min` peer is addressed by.

https://core.telegram.org/api/min. A check for one kind of peer has to accept that form too: a
channel one falling through to the non-channel branch calls a `messages.*` function on the
account's own private chats, and `delete_messages` deletes from them. A field typed
`InputUser`/`InputChannel` gets the matching `*FromMessage` constructor rather than the
`InputPeer` itself.
"""

from __future__ import annotations as _annotations

import inspect
from typing import TYPE_CHECKING, Any, Final

import pytest

from pyrogram import Client, raw, types, utils
from pyrogram.file_id import FileId

if TYPE_CHECKING:
    from collections.abc import Callable

    from pyrogram.raw.core import TLObject

_GROUP: Final[int] = 1234567
_CHANNEL: Final[int] = 7654321
_USER: Final[int] = 777001
_BASIC_GROUP: Final[int] = 42

_CHANNEL_ID: Final[int] = utils.get_channel_id(_CHANNEL)
_BASIC_GROUP_ID: Final[int] = -_BASIC_GROUP

# The supergroup both peers were seen in.
_SEEN_IN: Final = raw.types.InputPeerChannel(channel_id=_GROUP, access_hash=555)

_PEERS: Final[dict[int, raw.base.InputPeer]] = {
    _USER: raw.types.InputPeerUserFromMessage(peer=_SEEN_IN, msg_id=10, user_id=_USER),
    _CHANNEL_ID: raw.types.InputPeerChannelFromMessage(
        peer=_SEEN_IN, msg_id=10, channel_id=_CHANNEL
    ),
    _BASIC_GROUP_ID: raw.types.InputPeerChat(chat_id=_BASIC_GROUP),
}

_INPUT_USER: Final = raw.types.InputUserFromMessage(peer=_SEEN_IN, msg_id=10, user_id=_USER)
_INPUT_CHANNEL: Final = raw.types.InputChannelFromMessage(
    peer=_SEEN_IN, msg_id=10, channel_id=_CHANNEL
)


class _Sent(Exception):
    """Raised by the fake `invoke`, carrying the first query the method built."""

    def __init__(self, query: TLObject) -> None:
        self.query = query


@pytest.fixture
def resolved() -> list[int]:
    """Every id the client's `resolve_peer` was called with, in order."""
    return []


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, resolved: list[int]) -> Client:
    client = Client("from_message_probe", api_id=1, api_hash="0" * 32, in_memory=True)
    client.me = types.User(id=1, is_bot=False)

    async def resolve_peer(peer_id: int) -> raw.base.InputPeer:
        resolved.append(peer_id)

        return _PEERS[peer_id]

    async def invoke(query: TLObject, *args: Any, **kwargs: Any) -> None:
        raise _Sent(query)

    monkeypatch.setattr(client, "resolve_peer", resolve_peer)
    monkeypatch.setattr(client, "invoke", invoke)

    return client


async def first_query(call: Any) -> TLObject:
    """Run a method call, a coroutine or an async generator, up to its first request."""
    with pytest.raises(_Sent) as sent:
        if inspect.isasyncgen(call):
            async for _ in call:
                pass
        else:
            await call

    return sent.value.query


@pytest.mark.parametrize(
    ("call", "function", "field", "expected"),
    [
        (
            lambda c: c.get_messages(_CHANNEL_ID, 5),
            raw.functions.channels.GetMessages,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.delete_messages(_CHANNEL_ID, 5),
            raw.functions.channels.DeleteMessages,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.read_chat_history(_CHANNEL_ID),
            raw.functions.channels.ReadHistory,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.delete_chat_history(_CHANNEL_ID),
            raw.functions.channels.DeleteHistory,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.leave_chat(_CHANNEL_ID),
            raw.functions.channels.LeaveChannel,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.get_chat(_CHANNEL_ID),
            raw.functions.channels.GetFullChannel,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.get_chat(_CHANNEL_ID, force_full=False),
            raw.functions.channels.GetChannels,
            lambda q: q.id[0],
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.get_chat(_USER),
            raw.functions.users.GetFullUser,
            lambda q: q.id,
            _INPUT_USER,
        ),
        (
            lambda c: c.get_chat(_USER, force_full=False),
            raw.functions.users.GetUsers,
            lambda q: q.id[0],
            _INPUT_USER,
        ),
        (
            lambda c: c.get_users(_USER),
            raw.functions.users.GetUsers,
            lambda q: q.id[0],
            _INPUT_USER,
        ),
        (
            lambda c: c.get_chat_photos(_CHANNEL_ID),
            raw.functions.channels.GetFullChannel,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            # Straight to the photos: no request for an `access_hash` the photos do not use.
            lambda c: c.get_chat_photos(_USER),
            raw.functions.photos.GetUserPhotos,
            lambda q: q.user_id,
            _INPUT_USER,
        ),
        (
            lambda c: c.check_username(_CHANNEL_ID, "name"),
            raw.functions.channels.CheckUsername,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.get_chat_member(_CHANNEL_ID, _USER),
            raw.functions.channels.GetParticipant,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.ban_chat_member(_CHANNEL_ID, _USER),
            raw.functions.channels.EditBanned,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.set_slow_mode(_CHANNEL_ID, 10),
            raw.functions.channels.ToggleSlowMode,
            lambda q: q.channel,
            _INPUT_CHANNEL,
        ),
        (
            lambda c: c.add_contact(_USER, "name"),
            raw.functions.contacts.AddContact,
            lambda q: q.id,
            _INPUT_USER,
        ),
        (
            lambda c: c.get_common_chats(_USER),
            raw.functions.messages.GetCommonChats,
            lambda q: q.user_id,
            _INPUT_USER,
        ),
        (
            lambda c: c.set_game_score(_USER, 1, chat_id=_CHANNEL_ID, message_id=5),
            raw.functions.messages.SetGameScore,
            lambda q: q.user_id,
            _INPUT_USER,
        ),
    ],
    ids=[
        "get_messages",
        "delete_messages",
        "read_chat_history",
        "delete_chat_history",
        "leave_chat",
        "get_chat_full_channel",
        "get_chat_channel",
        "get_chat_full_user",
        "get_chat_user",
        "get_users",
        "get_chat_photos_channel",
        "get_chat_photos_user",
        "check_username",
        "get_chat_member",
        "ban_chat_member",
        "set_slow_mode",
        "add_contact",
        "get_common_chats",
        "set_game_score",
    ],
)
async def test_a_from_message_peer_reaches_the_right_function_in_the_right_form(
    client: Client,
    call: Callable[[Client], Any],
    function: type[TLObject],
    field: Callable[[TLObject], TLObject],
    expected: TLObject,
) -> None:
    query = await first_query(call(client))

    assert type(query) is function
    # Compared as bytes: `TLObject.__eq__` looks at the fields only, so the `InputPeer` the
    #  method was given would equal the `InputUser`/`InputChannel` the field needs.
    assert field(query).write() == expected.write()


async def test_ban_chat_member_still_refuses_a_private_chat(client: Client) -> None:
    with pytest.raises(ValueError, match="private chats"):
        await client.ban_chat_member(_USER, _USER)


async def test_leave_chat_resolves_the_chat_once(client: Client, resolved: list[int]) -> None:
    await first_query(client.leave_chat(_CHANNEL_ID))

    assert resolved == [_CHANNEL_ID]


async def test_a_basic_group_reaches_a_channel_field_unchanged(client: Client) -> None:
    # It has no `InputChannel` form. Sending it as it is leaves the server to reject it, as it
    #  did before any conversion.
    query = await first_query(client.set_slow_mode(_BASIC_GROUP_ID, 10))

    assert query.channel is _PEERS[_BASIC_GROUP_ID]


async def test_set_game_score_of_an_inline_message_sends_an_input_user(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Sent through the session of the message's DC rather than `Client.invoke`.
    class Session:
        async def invoke(self, query: TLObject, *args: Any, **kwargs: Any) -> None:
            raise _Sent(query)

    async def get_session(*args: Any, **kwargs: Any) -> Session:
        return Session()

    monkeypatch.setattr(client, "get_session", get_session)

    inline_message_id = utils.pack_inline_message_id(
        raw.types.InputBotInlineMessageID(dc_id=2, id=1, access_hash=3)
    )
    query = await first_query(client.set_game_score(_USER, 1, inline_message_id=inline_message_id))

    assert isinstance(query, raw.functions.messages.SetInlineGameScore)
    assert query.user_id.write() == _INPUT_USER.write()


def a_photo_without_a_concrete_size() -> raw.types.Photo:
    # Only a stripped preview: `ChatPhoto._parse()` then keeps the `CHAT_PHOTO` ids, which
    #  download through the peer and so carry its `access_hash`.
    return raw.types.Photo(
        id=1,
        access_hash=2,
        file_reference=b"",
        date=0,
        sizes=[raw.types.PhotoStrippedSize(type="i", bytes=b"")],
        dc_id=2,
    )


async def test_get_chat_photos_takes_a_min_users_access_hash_from_the_answer(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A `*FromMessage` peer carries none. The answer's `users` hold the `min` one, which is
    #  still valid for profile photos, so no request is made for it.
    queries: list[TLObject] = []

    async def invoke(query: TLObject, *args: Any, **kwargs: Any) -> raw.types.photos.Photos:
        queries.append(query)

        return raw.types.photos.Photos(
            photos=[a_photo_without_a_concrete_size()],
            users=[raw.types.User(id=_USER, min=True, access_hash=99, usernames=[])],
        )

    monkeypatch.setattr(client, "invoke", invoke)

    (photo,) = [photo async for photo in client.get_chat_photos(_USER, limit=1)]

    assert FileId.decode(photo.big_file_id).chat_access_hash == 99
    assert [type(query) for query in queries] == [raw.functions.photos.GetUserPhotos]


async def test_get_chat_photos_takes_a_min_channels_access_hash_from_the_answer(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def invoke(query: TLObject, *args: Any, **kwargs: Any) -> raw.types.messages.ChatFull:
        assert isinstance(query, raw.functions.channels.GetFullChannel)

        return raw.types.messages.ChatFull(
            full_chat=raw.types.ChannelFull(
                id=_CHANNEL,
                about="",
                read_inbox_max_id=0,
                read_outbox_max_id=0,
                unread_count=0,
                chat_photo=a_photo_without_a_concrete_size(),
                notify_settings=raw.types.PeerNotifySettings(),
                bot_info=[],
                pts=0,
            ),
            chats=[
                raw.types.Channel(
                    id=_CHANNEL,
                    title="c",
                    photo=raw.types.ChatPhotoEmpty(),
                    date=0,
                    min=True,
                    access_hash=77,
                    usernames=[],
                    restriction_reason=[],
                )
            ],
            users=[],
        )

    monkeypatch.setattr(client, "invoke", invoke)

    (photo,) = [photo async for photo in client.get_chat_photos(_CHANNEL_ID, limit=1)]

    assert FileId.decode(photo.big_file_id).chat_access_hash == 77
