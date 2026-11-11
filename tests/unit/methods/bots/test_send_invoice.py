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

from typing import TYPE_CHECKING

import pytest

from pyrogram import raw, types

if TYPE_CHECKING:
    from pyrogram import Client

    from .conftest import Capture


@pytest.mark.parametrize(
    ("max_tip_amount", "suggested_tip_amounts", "expected"),
    [
        # Tips alone set `flags.8`, and the `long` it gates was `None`, so `write()` raised.
        pytest.param(None, [100], 0, id="tips-only"),
        pytest.param(500, [100], 500, id="both"),
        pytest.param(500, None, 500, id="maximum-only"),
        pytest.param(None, None, None, id="neither"),
    ],
)
async def test_the_tip_maximum_is_written_whenever_tips_are(
    client: Client,
    capture: Capture,
    *,
    max_tip_amount: int | None,
    suggested_tip_amounts: list[int] | None,
    expected: int | None,
) -> None:
    request = await capture(
        client.send_invoice(
            chat_id=1,
            title="title",
            description="description",
            payload="payload",
            currency="USD",
            prices=[
                types.LabeledPrice(
                    label="item",
                    amount=100,
                )
            ],
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
        )
    )

    assert isinstance(request, raw.functions.messages.SendMedia)
    assert request.media.invoice.max_tip_amount == expected
    request.write()
