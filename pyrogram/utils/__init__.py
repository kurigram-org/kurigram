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

from .amounts import (
    from_nano,
    get_premium_duration_day_count,
    get_premium_duration_month_count,
    to_nano,
)
from .cache import Cache
from .console import ainput
from .crypto import btoi, compute_password_check, compute_password_hash, itob, sha256, xor
from .datetimes import datetime_to_timestamp, max_datetime, timestamp_to_datetime, zero_datetime
from .file_ids import (
    expand_inline_bytes,
    from_inline_bytes,
    get_file_name,
    get_input_media_from_file_id,
)
from .gifts import get_input_stargift
from .inline import pack_inline_message_id, unpack_inline_message_id
from .json_values import jsonvalue_to_obj, obj_to_jsonvalue
from .messages import get_reply_to, parse_deleted_messages, parse_messages
from .parsing import require_parsed
from .peers import (
    MAX_CHANNEL_ID,
    MAX_CHAT_ID,
    MAX_MONOFORUM_CHANNEL_ID,
    MAX_USER_ID,
    MIN_MONOFORUM_CHANNEL_ID,
    PEERS_WITH_A_CHANNEL_ID,
    PEERS_WITH_A_CHAT_ID,
    PEERS_WITH_A_USER_ID,
    ZERO_CHANNEL_ID,
    ZERO_SECRET_CHAT_ID,
    get_channel_id,
    get_peer_id,
    get_peer_type,
    get_raw_peer_id,
)
from .text import get_first_url, parse_text_entities, parse_text_with_entities, split_text

__all__ = [
    "Cache",
    "MAX_CHANNEL_ID",
    "MAX_CHAT_ID",
    "MAX_MONOFORUM_CHANNEL_ID",
    "MAX_USER_ID",
    "MIN_MONOFORUM_CHANNEL_ID",
    "PEERS_WITH_A_CHANNEL_ID",
    "PEERS_WITH_A_CHAT_ID",
    "PEERS_WITH_A_USER_ID",
    "ZERO_CHANNEL_ID",
    "ZERO_SECRET_CHAT_ID",
    "ainput",
    "btoi",
    "compute_password_check",
    "compute_password_hash",
    "datetime_to_timestamp",
    "expand_inline_bytes",
    "from_inline_bytes",
    "from_nano",
    "get_channel_id",
    "get_file_name",
    "get_first_url",
    "get_input_media_from_file_id",
    "get_input_stargift",
    "get_peer_id",
    "get_peer_type",
    "get_premium_duration_day_count",
    "get_premium_duration_month_count",
    "get_raw_peer_id",
    "get_reply_to",
    "itob",
    "jsonvalue_to_obj",
    "max_datetime",
    "obj_to_jsonvalue",
    "pack_inline_message_id",
    "parse_deleted_messages",
    "parse_messages",
    "parse_text_entities",
    "parse_text_with_entities",
    "require_parsed",
    "sha256",
    "split_text",
    "timestamp_to_datetime",
    "to_nano",
    "unpack_inline_message_id",
    "xor",
    "zero_datetime",
]
