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

from pyrogram import raw
from pyrogram.types import Chat


@pytest.mark.asyncio
async def test_a_full_chat_the_library_cannot_read_raises() -> None:
    # The three branches of `_parse_full()` cover every answer the schema allows to the three
    #  calls that reach it, so a fourth shape means the layer moved under us. There was no
    #  `else`: such an answer fell off the end as `None`, and `get_chat()` handed that to the
    #  caller, who met it as an `AttributeError` frames away from the call that produced it.
    unreadable = raw.types.messages.ChatFull(
        full_chat=raw.types.ChatEmpty(id=1),
        chats=[],
        users=[],
    )

    with pytest.raises(ValueError, match="Unknown full chat type: ChatEmpty"):
        await Chat._parse_full(None, unreadable)


@pytest.mark.asyncio
async def test_an_empty_chat_is_no_chat_rather_than_a_channel() -> None:
    # `chatEmpty` and `userEmpty` are TL constructors of their own, not subclasses of `chat`
    #  and `user`, so `_parse_chat()` dropped both into its channel branch, which read a flag
    #  off them: `AttributeError: 'ChatEmpty' object has no attribute 'monoforum'`.
    assert await Chat._parse_chat(None, raw.types.ChatEmpty(id=1)) is None
    assert await Chat._parse_chat(None, raw.types.UserEmpty(id=1)) is None
