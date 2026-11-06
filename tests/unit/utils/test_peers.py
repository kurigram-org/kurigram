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
from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest

from pyrogram import raw
from pyrogram.utils.peers import (
    PEERS_WITH_A_CHANNEL_ID,
    PEERS_WITH_A_CHAT_ID,
    PEERS_WITH_A_USER_ID,
    get_input_user_or_channel,
    get_peer_id,
    get_raw_peer_id,
)

if TYPE_CHECKING:
    from pyrogram.raw.core import TLObject

_SCHEMA: Final[Path] = (
    Path(__file__).resolve().parents[3] / "compiler" / "api" / "source" / "main_api.tl"
)

_PEER_CONSTRUCTOR: Final[re.Pattern[str]] = re.compile(
    r"^(?P<name>\w+)#[0-9a-f]+ (?P<fields>.*)= (?:Peer|InputPeer|RequestedPeer);$",
    re.MULTILINE,
)

_EMPTY_INPUT_PEER: Final = raw.types.InputPeerEmpty()


@pytest.mark.parametrize(
    ("peer", "expected"),
    [
        pytest.param(raw.types.PeerUser(user_id=10), 10, id="peer-user"),
        pytest.param(
            raw.types.InputPeerUser(
                user_id=10,
                access_hash=0,
            ),
            10,
            id="input-peer-user",
        ),
        pytest.param(
            raw.types.InputPeerUserFromMessage(
                peer=_EMPTY_INPUT_PEER,
                msg_id=1,
                user_id=10,
            ),
            10,
            id="input-peer-user-from-message",
        ),
        pytest.param(raw.types.RequestedPeerUser(user_id=10), 10, id="requested-peer-user"),
        pytest.param(raw.types.PeerChat(chat_id=20), 20, id="peer-chat"),
        pytest.param(raw.types.InputPeerChat(chat_id=20), 20, id="input-peer-chat"),
        pytest.param(raw.types.RequestedPeerChat(chat_id=20), 20, id="requested-peer-chat"),
        pytest.param(raw.types.PeerChannel(channel_id=30), 30, id="peer-channel"),
        pytest.param(
            raw.types.InputPeerChannel(
                channel_id=30,
                access_hash=0,
            ),
            30,
            id="input-peer-channel",
        ),
        pytest.param(
            raw.types.InputPeerChannelFromMessage(
                peer=_EMPTY_INPUT_PEER,
                msg_id=1,
                channel_id=30,
            ),
            30,
            id="input-peer-channel-from-message",
        ),
        pytest.param(
            raw.types.RequestedPeerChannel(channel_id=30),
            30,
            id="requested-peer-channel",
        ),
        pytest.param(raw.types.InputPeerSelf(), None, id="input-peer-self"),
        pytest.param(10, 10, id="user-id"),
        pytest.param(-20, 20, id="chat-id"),
        pytest.param(-1000000000030, 30, id="channel-id"),
        pytest.param(-3000000000000, 2000000000000, id="monoforum-id"),
        pytest.param(0, None, id="zero"),
    ],
)
def test_get_raw_peer_id(
    peer: int | raw.base.Peer | raw.base.InputPeer | raw.base.RequestedPeer,
    *,
    expected: int | None,
) -> None:
    assert get_raw_peer_id(peer) == expected


@pytest.mark.parametrize(
    ("peer", "expected"),
    [
        pytest.param(raw.types.PeerUser(user_id=10), 10, id="user"),
        pytest.param(raw.types.PeerChat(chat_id=20), -20, id="chat"),
        pytest.param(raw.types.PeerChannel(channel_id=30), -1000000000030, id="channel"),
    ],
)
def test_get_peer_id(
    peer: raw.base.Peer,
    *,
    expected: int,
) -> None:
    assert get_peer_id(peer) == expected


def test_get_peer_id_rejects_a_peer_without_an_id() -> None:
    with pytest.raises(ValueError, match="Peer type invalid"):
        get_peer_id(raw.types.InputPeerSelf())


# A constructor a new layer adds with an id field would otherwise fall through both
#  functions: `get_raw_peer_id` returns `None`, `get_peer_id` raises.
@pytest.mark.parametrize(
    ("attribute", "peers"),
    [
        pytest.param("user_id", PEERS_WITH_A_USER_ID, id="user"),
        pytest.param("chat_id", PEERS_WITH_A_CHAT_ID, id="chat"),
        pytest.param("channel_id", PEERS_WITH_A_CHANNEL_ID, id="channel"),
    ],
)
def test_peer_tuples_match_the_schema(
    attribute: str,
    *,
    peers: tuple[type[TLObject], ...],
) -> None:
    schema = _SCHEMA.read_text()
    expected_constructors = {
        match["name"][0].upper() + match["name"][1:]
        for match in _PEER_CONSTRUCTOR.finditer(schema)
        if f" {attribute}:" in f" {match['fields']}"
    }

    assert {peer.__name__ for peer in peers} == expected_constructors


_SEEN_IN: Final = raw.types.InputPeerChannel(channel_id=5, access_hash=55)


@pytest.mark.parametrize(
    ("peer", "expected"),
    [
        pytest.param(
            raw.types.InputPeerUser(user_id=1, access_hash=11),
            raw.types.InputUser(user_id=1, access_hash=11),
            id="input-peer-user",
        ),
        pytest.param(
            raw.types.InputPeerUserFromMessage(peer=_SEEN_IN, msg_id=7, user_id=1),
            raw.types.InputUserFromMessage(peer=_SEEN_IN, msg_id=7, user_id=1),
            id="input-peer-user-from-message",
        ),
        pytest.param(raw.types.InputPeerSelf(), raw.types.InputUserSelf(), id="input-peer-self"),
        pytest.param(
            raw.types.InputPeerChannel(channel_id=2, access_hash=22),
            raw.types.InputChannel(channel_id=2, access_hash=22),
            id="input-peer-channel",
        ),
        pytest.param(
            raw.types.InputPeerChannelFromMessage(peer=_SEEN_IN, msg_id=7, channel_id=2),
            raw.types.InputChannelFromMessage(peer=_SEEN_IN, msg_id=7, channel_id=2),
            id="input-peer-channel-from-message",
        ),
    ],
)
def test_get_input_user_or_channel_converts_a_user_or_channel_peer(
    peer: raw.base.InputPeer,
    *,
    expected: raw.base.InputUser | raw.base.InputChannel,
) -> None:
    # Compared as bytes: `TLObject.__eq__` looks at the fields only, so an `InputPeerUser`
    #  equals the `InputUser` with the same ones. The bytes start with the constructor id,
    #  which is what the server tells the two apart by.
    assert get_input_user_or_channel(peer).write() == expected.write()


@pytest.mark.parametrize(
    "peer",
    [
        pytest.param(raw.types.InputUser(user_id=1, access_hash=11), id="input-user"),
        pytest.param(
            raw.types.InputUserFromMessage(peer=_SEEN_IN, msg_id=7, user_id=1),
            id="input-user-from-message",
        ),
        pytest.param(raw.types.InputUserSelf(), id="input-user-self"),
        pytest.param(raw.types.InputUserEmpty(), id="input-user-empty"),
        pytest.param(raw.types.InputChannel(channel_id=2, access_hash=22), id="input-channel"),
        pytest.param(
            raw.types.InputChannelFromMessage(peer=_SEEN_IN, msg_id=7, channel_id=2),
            id="input-channel-from-message",
        ),
        pytest.param(raw.types.InputChannelEmpty(), id="input-channel-empty"),
    ],
)
def test_get_input_user_or_channel_returns_an_input_form_as_is(
    peer: raw.base.InputUser | raw.base.InputChannel,
) -> None:
    # A variable that may hold either form, like a pagination offset starting at
    #  `InputUserEmpty`, can go through without a check of its own.
    assert get_input_user_or_channel(peer) is peer


@pytest.mark.parametrize(
    "peer",
    [
        pytest.param(raw.types.InputPeerChat(chat_id=3), id="input-peer-chat"),
        pytest.param(_EMPTY_INPUT_PEER, id="input-peer-empty"),
    ],
)
def test_get_input_user_or_channel_leaves_a_peer_without_either_form_to_the_server(
    peer: raw.base.InputPeer,
) -> None:
    # A basic group has neither form and an empty peer could be either. Passing them on keeps
    #  the server's own error, as before the conversion existed.
    assert get_input_user_or_channel(peer) is peer
