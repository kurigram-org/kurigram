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

from pyrogram import raw, types


def test_a_chat_location_without_a_point_keeps_its_address() -> None:
    location = raw.types.ChannelLocation(
        geo_point=raw.types.GeoPointEmpty(),
        address="Somewhere",
    )

    parsed = types.Location._parse(location)

    assert (parsed.longitude, parsed.latitude, parsed.address) == (None, None, "Somewhere")
