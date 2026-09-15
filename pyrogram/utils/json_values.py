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

from pyrogram import raw


def obj_to_jsonvalue(obj) -> raw.base.JSONValue:
    if obj is None:
        return raw.types.JsonNull()
    elif isinstance(obj, bool):
        return raw.types.JsonBool(value=obj)
    elif isinstance(obj, (int, float)):
        return raw.types.JsonNumber(value=obj)
    elif isinstance(obj, str):
        return raw.types.JsonString(value=obj)
    elif isinstance(obj, (list, tuple)):
        return raw.types.JsonArray(value=[obj_to_jsonvalue(x) for x in obj])
    elif isinstance(obj, dict):
        return raw.types.JsonObject(
            value=[
                raw.types.JsonObjectValue(key=k, value=obj_to_jsonvalue(v)) for k, v in obj.items()
            ]
        )

    raise TypeError(f"Unsupported type: {type(obj)}")


def jsonvalue_to_obj(obj: raw.base.JSONValue):
    if isinstance(obj, raw.types.JsonNull):
        return None
    elif isinstance(obj, raw.types.JsonBool):
        return obj.value
    elif isinstance(obj, raw.types.JsonNumber):
        return obj.value
    elif isinstance(obj, raw.types.JsonString):
        return obj.value
    elif isinstance(obj, raw.types.JsonArray):
        return [jsonvalue_to_obj(x) for x in obj.value]
    elif isinstance(obj, raw.types.JsonObject):
        return {o.key: jsonvalue_to_obj(o.value) for o in obj.value}

    raise TypeError(f"Unsupported type: {type(obj)}")
