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
from pyrogram import enums, raw, types

from ..object import Object


class GiftAttribute(Object):
    """Contains information about a star gift attribute.

    Parameters:
        type (:obj:`~pyrogram.enums.GiftAttributeType`):
            Type of the attribute.

        name (``str``, *optional*):
            Name of the attribute.

        backdrop_id (``int``, *optional*):
            Unique backdrop identifier.
            Available only if the backdrop attribute is available.

        rarity (:obj:`~pyrogram.types.UpgradedGiftAttributeRarityPerMille` | :obj:`~pyrogram.types.UpgradedGiftAttributeRarityUncommon` | :obj:`~pyrogram.types.UpgradedGiftAttributeRarityRare` | :obj:`~pyrogram.types.UpgradedGiftAttributeRarityEpic` | :obj:`~pyrogram.types.UpgradedGiftAttributeRarityLegendary`, *optional*):
            The rarity of the model.

        center_color (``int``, *optional*):
            Center color of the gift in decimal format.
            Available only if the backdrop attribute is available.

        edge_color (``int``, *optional*):
            Edge color of the gift in decimal format.
            Available only if the backdrop attribute is available.

        pattern_color (``int``, *optional*):
            Pattern color of the gift in decimal format.
            Available only if the backdrop attribute is available.

        text_color (``int``, *optional*):
            Text color of the gift in decimal format.
            Available only if the backdrop attribute is available.

        sticker (:obj:`~pyrogram.types.Sticker`, *optional*):
            Information about the sticker.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        type: enums.GiftAttributeType,
        name: str | None = None,
        backdrop_id: int | None = None,
        rarity: (
            types.UpgradedGiftAttributeRarityPerMille
            | types.UpgradedGiftAttributeRarityUncommon
            | types.UpgradedGiftAttributeRarityRare
            | types.UpgradedGiftAttributeRarityEpic
            | types.UpgradedGiftAttributeRarityLegendary
            | None
        ) = None,
        sticker: types.Sticker | None = None,
        center_color: int | None = None,
        edge_color: int | None = None,
        pattern_color: int | None = None,
        text_color: int | None = None,
    ):
        super().__init__(client)

        self.name = name
        self.backdrop_id = backdrop_id
        self.type = type
        self.rarity = rarity
        self.sticker = sticker
        self.center_color = center_color
        self.edge_color = edge_color
        self.pattern_color = pattern_color
        self.text_color = text_color

    @staticmethod
    async def _parse(
        client,
        attr: raw.base.StarGiftAttribute,
    ) -> GiftAttribute:
        sticker = None

        if hasattr(attr, "document"):
            doc = attr.document
            attributes = {type(i): i for i in doc.attributes}
            sticker = await types.Sticker._parse(client, doc, attributes)

        return GiftAttribute(
            name=getattr(attr, "name", None),
            backdrop_id=getattr(attr, "backdrop_id", None),
            type=enums.GiftAttributeType(type(attr)),
            rarity=types.UpgradedGiftAttributeRarity._parse(attr.rarity),
            sticker=sticker,
            center_color=getattr(attr, "center_color", None),
            edge_color=getattr(attr, "edge_color", None),
            pattern_color=getattr(attr, "pattern_color", None),
            text_color=getattr(attr, "text_color", None),
            client=client,
        )
