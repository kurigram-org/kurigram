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

import pyrogram
from pyrogram import raw


async def get_input_stargift(
    client: pyrogram.Client, owned_gift_id: str
) -> raw.base.InputSavedStarGift:
    if not isinstance(owned_gift_id, str):
        raise ValueError(f"owned_gift_id has to be str, but {type(owned_gift_id)} was provided")

    saved_gift_match = client.SAVED_GIFT_RE.match(owned_gift_id)
    slug_match = client.UPGRADED_GIFT_RE.match(owned_gift_id)

    if saved_gift_match:
        return raw.types.InputSavedStarGiftChat(
            peer=await client.resolve_peer(int(saved_gift_match.group(1))),
            saved_id=int(saved_gift_match.group(2)),
        )
    elif slug_match:
        return raw.types.InputSavedStarGiftSlug(slug=slug_match.group(1))
    else:
        return raw.types.InputSavedStarGiftUser(msg_id=int(owned_gift_id))
