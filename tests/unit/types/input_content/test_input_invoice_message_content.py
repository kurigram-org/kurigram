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

import io

import pytest

import pyrogram
from pyrogram import raw, types


@pytest.mark.asyncio
async def test_an_invoice_without_a_provider_token_writes_an_empty_provider() -> None:
    # `provider_token` is optional, but `inputBotInlineMessageMediaInvoice.provider` is a plain
    #  `string`, so leaving it out failed on `None.encode()` in `answer_inline_query()`.
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )
    content = types.InputInvoiceMessageContent(
        title="Title",
        description="Description",
        payload="payload",
        currency="XTR",
        prices=[
            types.LabeledPrice(
                label="Item",
                amount=1,
            ),
        ],
    )

    message = await content.write(client, None)

    written = raw.core.TLObject.read(io.BytesIO(message.write()))

    assert written.provider == ""
