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

import inspect
from typing import Final

import pytest

from pyrogram import raw, types, utils

_USER_ID: Final[int] = 1
_CHANNEL_ID: Final[int] = 2
# Neither in `users` nor in `chats`, the case where `_parse()` leaves a side `None`.
_UNKNOWN_ID: Final[int] = 3

_USER: Final[raw.types.User] = raw.types.User(
    id=_USER_ID,
    first_name="Traveler",
)
_CHANNEL: Final[raw.types.Channel] = raw.types.Channel(
    id=_CHANNEL_ID,
    title="Watcher",
    photo=raw.types.ChatPhotoEmpty(),
    date=0,
    broadcast=True,
    # Deserialization fills an absent vector with `[]` (`compiler/api/compiler.py:604`), the
    #  constructor leaves `None`, and `Chat._parse_channel_chat` iterates both unguarded:
    #  `TypeError: 'NoneType' object is not iterable`.
    restriction_reason=[],
    usernames=[],
)

# A channel's `Chat.id` is the `-100`-prefixed form, so the id alone tells which raw peer was parsed.
_CHANNEL_CHAT_ID: Final[int] = utils.get_channel_id(_CHANNEL_ID)


async def parse_alert(
    *,
    from_id: raw.base.Peer,
    to_id: raw.base.Peer,
) -> types.ProximityAlertTriggered:
    action = raw.types.MessageActionGeoProximityReached(
        from_id=from_id,
        to_id=to_id,
        distance=50,
    )

    return await types.ProximityAlertTriggered._parse(
        None,
        action,
        {_USER_ID: _USER},
        {_CHANNEL_ID: _CHANNEL},
    )


@pytest.mark.parametrize(
    ("from_id", "to_id", "expected_ids"),
    [
        pytest.param(
            raw.types.PeerUser(user_id=_USER_ID),
            raw.types.PeerChannel(channel_id=_CHANNEL_ID),
            [_USER_ID, _CHANNEL_CHAT_ID],
            id="user-travels-channel-watches",
        ),
        pytest.param(
            raw.types.PeerChannel(channel_id=_CHANNEL_ID),
            raw.types.PeerUser(user_id=_USER_ID),
            [_CHANNEL_CHAT_ID, _USER_ID],
            id="channel-travels-user-watches",
        ),
    ],
)
async def test_either_side_parses_to_a_chat(
    from_id: raw.base.Peer,
    to_id: raw.base.Peer,
    *,
    expected_ids: list[int],
) -> None:
    alert = await parse_alert(
        from_id=from_id,
        to_id=to_id,
    )

    assert alert.traveler is not None
    assert alert.watcher is not None
    assert [alert.traveler.id, alert.watcher.id] == expected_ids
    assert alert.distance == 50


@pytest.mark.parametrize(
    "to_id",
    [
        pytest.param(raw.types.PeerChannel(channel_id=_CHANNEL_ID), id="both-sides-known"),
        pytest.param(raw.types.PeerUser(user_id=_UNKNOWN_ID), id="watcher-unknown"),
    ],
)
async def test_every_field_is_what_the_signature_annotates(to_id: raw.base.Peer) -> None:
    # The parse above passes whatever the annotations say, so this is what pins them: the
    #  `User` and `str` they used to promise fail `isinstance` against the `Chat` and `int` built,
    #  and a bare `Chat` fails it against the `None` an unknown peer parses to.
    alert = await parse_alert(
        from_id=raw.types.PeerUser(user_id=_USER_ID),
        to_id=to_id,
    )
    signature = inspect.signature(types.ProximityAlertTriggered.__init__, eval_str=True)

    assert {
        name: isinstance(getattr(alert, name), parameter.annotation)
        for name, parameter in signature.parameters.items()
        if name != "self"
    } == {"traveler": True, "watcher": True, "distance": True}
