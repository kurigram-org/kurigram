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

from typing import Final

from pyrogram import raw

ZERO_SECRET_CHAT_ID = -2000000000000
ZERO_CHANNEL_ID = -1000000000000

MAX_CHANNEL_ID = 1000000000000 - (1 << 31)
MIN_MONOFORUM_CHANNEL_ID = 1000000000000 + (1 << 31) + 1
MAX_MONOFORUM_CHANNEL_ID = 3000000000000
MAX_USER_ID = (1 << 40) - 1
MAX_CHAT_ID = 999999999999

# The constructors of `Peer`/`InputPeer`/`RequestedPeer` that carry each id attribute;
#  `isinstance` over them is what lets a type checker narrow the attribute type.
PEERS_WITH_A_USER_ID: Final = (
    raw.types.PeerUser,
    raw.types.InputPeerUser,
    raw.types.InputPeerUserFromMessage,
    raw.types.RequestedPeerUser,
)

PEERS_WITH_A_CHAT_ID: Final = (
    raw.types.PeerChat,
    raw.types.InputPeerChat,
    raw.types.RequestedPeerChat,
)

PEERS_WITH_A_CHANNEL_ID: Final = (
    raw.types.PeerChannel,
    raw.types.InputPeerChannel,
    raw.types.InputPeerChannelFromMessage,
    raw.types.RequestedPeerChannel,
)


def get_raw_peer_id(
    peer: int | raw.base.Peer | raw.base.InputPeer | raw.base.RequestedPeer,
) -> int | None:
    """Get the raw peer id from a Peer object or high-lvl id"""

    if isinstance(peer, int):
        if peer < 0:
            if -MAX_CHAT_ID <= peer:
                return -peer

            if ZERO_CHANNEL_ID - MAX_CHANNEL_ID <= peer and peer != ZERO_CHANNEL_ID:
                return ZERO_CHANNEL_ID - peer

            if ZERO_CHANNEL_ID - MAX_MONOFORUM_CHANNEL_ID <= peer:
                return ZERO_CHANNEL_ID - peer

        elif 0 < peer <= MAX_USER_ID:
            return peer
    else:
        if isinstance(peer, PEERS_WITH_A_USER_ID):
            return peer.user_id

        if isinstance(peer, PEERS_WITH_A_CHAT_ID):
            return peer.chat_id

        if isinstance(peer, PEERS_WITH_A_CHANNEL_ID):
            return peer.channel_id

    return None


def get_peer_id(peer: raw.base.Peer | raw.base.InputPeer | raw.base.RequestedPeer) -> int:
    """Get the non-raw peer id from a Peer object"""
    if isinstance(peer, PEERS_WITH_A_USER_ID):
        return peer.user_id

    if isinstance(peer, PEERS_WITH_A_CHAT_ID):
        return -peer.chat_id

    if isinstance(peer, PEERS_WITH_A_CHANNEL_ID):
        return ZERO_CHANNEL_ID - peer.channel_id

    raise ValueError(f"Peer type invalid: {peer}")


def get_peer_type(peer_id: int) -> str:
    if peer_id < 0:
        if -MAX_CHAT_ID <= peer_id:
            return "chat"

        if ZERO_CHANNEL_ID - MAX_CHANNEL_ID <= peer_id and peer_id != ZERO_CHANNEL_ID:
            return "channel"

        if ZERO_SECRET_CHAT_ID + (-1 << 31) <= peer_id and peer_id != ZERO_SECRET_CHAT_ID:
            return "secret_chat"

        if ZERO_CHANNEL_ID - MAX_MONOFORUM_CHANNEL_ID <= peer_id:
            return "monoforum"

    elif 0 < peer_id <= MAX_USER_ID:
        return "user"

    raise ValueError(f"Peer id invalid: {peer_id}")


def get_channel_id(peer_id: int) -> int:
    return ZERO_CHANNEL_ID - peer_id


def get_input_user_or_channel(
    peer: raw.base.InputPeer | raw.base.InputUser | raw.base.InputChannel,
) -> raw.base.InputPeer | raw.base.InputUser | raw.base.InputChannel:
    """Get the `InputUser` or `InputChannel` of a peer, for the fields that expect one.

    A user peer gives an `InputUser` and a channel peer an `InputChannel`, a `*FromMessage`
    one, which is how a `min` peer is addressed (https://core.telegram.org/api/min), keeping
    its form. Anything else is returned as is: a value that already is one of them, and a peer
    that has neither form, which the server then rejects as it did before this conversion.
    """
    if isinstance(peer, raw.types.InputPeerUser):
        return raw.types.InputUser(user_id=peer.user_id, access_hash=peer.access_hash)

    if isinstance(peer, raw.types.InputPeerUserFromMessage):
        return raw.types.InputUserFromMessage(
            peer=peer.peer, msg_id=peer.msg_id, user_id=peer.user_id
        )

    if isinstance(peer, raw.types.InputPeerSelf):
        return raw.types.InputUserSelf()

    if isinstance(peer, raw.types.InputPeerChannel):
        return raw.types.InputChannel(channel_id=peer.channel_id, access_hash=peer.access_hash)

    if isinstance(peer, raw.types.InputPeerChannelFromMessage):
        return raw.types.InputChannelFromMessage(
            peer=peer.peer, msg_id=peer.msg_id, channel_id=peer.channel_id
        )

    # Already an `InputUser` or `InputChannel`, or `InputPeerChat` with neither form, or
    #  `InputPeerEmpty` that could be either.
    return peer
