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


_SENDER_ID: Final[int] = 7


@pytest.mark.parametrize(
    ("users", "expected"),
    [
        pytest.param({}, None, id="missing"),
        pytest.param(
            {
                _SENDER_ID: raw.types.User(
                    id=_SENDER_ID,
                    first_name="Sender",
                ),
            },
            _SENDER_ID,
            id="known",
        ),
    ],
)
@pytest.mark.asyncio
async def test_a_transfer_names_its_sender_only_when_users_has_it(
    users: dict[int, raw.base.User],
    *,
    expected: int | None,
) -> None:
    action = raw.types.MessageActionGramTransfer(
        amount=1,
        peer_address="address",
        transaction_id="transaction",
    )
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )

    parsed = await types.TonWalletTransfer._parse(client, action, _SENDER_ID, users)

    assert getattr(parsed.sender, "id", None) == expected
