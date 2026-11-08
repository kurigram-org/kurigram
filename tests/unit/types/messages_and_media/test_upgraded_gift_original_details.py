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

import pytest

import pyrogram
from pyrogram import raw, types

_RAW_ID: Final[int] = 7


@pytest.mark.parametrize(
    ("peer", "expected"),
    [
        pytest.param(raw.types.PeerChannel(channel_id=_RAW_ID), (None, None), id="channel"),
        pytest.param(raw.types.PeerUser(user_id=_RAW_ID), (_RAW_ID, _RAW_ID), id="user"),
    ],
)
@pytest.mark.asyncio
async def test_only_a_user_peer_is_taken_for_a_user(
    peer: raw.base.Peer,
    *,
    expected: tuple[int | None, int | None],
) -> None:
    # User and channel ids overlap, so a lookup by raw id alone took a channel for the user.
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )
    user = raw.types.User(
        id=_RAW_ID,
        first_name="User",
        access_hash=0,
    )
    details = raw.types.StarGiftAttributeOriginalDetails(
        sender_id=peer,
        recipient_id=peer,
        date=1,
    )

    parsed = await types.UpgradedGiftOriginalDetails._parse(
        client,
        details,
        {_RAW_ID: user},
        {},
    )

    assert (
        parsed.sender.id if parsed.sender else None,
        parsed.receiver.id if parsed.receiver else None,
    ) == expected
