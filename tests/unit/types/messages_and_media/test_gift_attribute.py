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

from pyrogram import enums, raw, types


async def test_a_backdrop_attribute_parses_into_every_backdrop_field() -> None:
    backdrop = raw.types.StarGiftAttributeBackdrop(
        name="Onyx",
        backdrop_id=7,
        center_color=1,
        edge_color=2,
        pattern_color=3,
        text_color=4,
        rarity=raw.types.StarGiftAttributeRarity(permille=15),
    )

    parsed = await types.GiftAttribute._parse(None, backdrop)

    assert parsed == types.GiftAttribute(
        type=enums.GiftAttributeType.BACKDROP,
        name="Onyx",
        backdrop_id=7,
        rarity=types.UpgradedGiftAttributeRarityPerMille(per_mille=15),
        center_color=1,
        edge_color=2,
        pattern_color=3,
        text_color=4,
    )
