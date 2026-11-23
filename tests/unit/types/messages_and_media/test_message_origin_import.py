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

from pyrogram import enums, types


def test_message_origin_import_takes_its_documented_type() -> None:
    # Not the default, so a `type` taken and then dropped fails here.
    origin = types.MessageOriginImport(type=enums.MessageOriginType.USER)

    assert origin.type is enums.MessageOriginType.USER


def test_message_origin_import_defaults_type_to_import() -> None:
    origin = types.MessageOriginImport(sender_user_name="Alice")

    assert origin.type is enums.MessageOriginType.IMPORT
