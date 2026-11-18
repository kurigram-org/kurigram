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

from pyrogram import Client, raw, types


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
    *,
    max_tip_amount: int | None,
    suggested_tip_amounts: list[int] | None,
    expected: int | None,
) -> None:
    content = types.InputInvoiceMessageContent(
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
        provider_token="changeme",
        max_tip_amount=max_tip_amount,
        suggested_tip_amounts=suggested_tip_amounts,
    )

    message = await content.write(
        Client(
            name="invoice_content",
            in_memory=True,
        ),
        None,
    )

    assert isinstance(message, raw.types.InputBotInlineMessageMediaInvoice)
    assert message.invoice.max_tip_amount == expected
    message.write()
