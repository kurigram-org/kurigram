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

import re

import pyrogram
from pyrogram import enums, raw, types
from pyrogram.types.messages_and_media.message import Str


async def parse_text_entities(
    client: pyrogram.Client,
    text: str,
    parse_mode: enums.ParseMode | None,
    entities: list[types.MessageEntity] | None,
) -> dict[str, str | list[raw.base.MessageEntity] | None]:
    if entities:
        # Inject the client instance because parsing user mentions requires it
        for entity in entities:
            entity._client = client

        raw_entities: list[raw.base.MessageEntity] | None = [
            await entity.write() for entity in entities
        ] or None
    else:
        text, raw_entities = (await client.parser.parse(text, parse_mode)).values()

    return {"message": text, "entities": raw_entities}


async def parse_text_with_entities(client, message: raw.types.TextWithEntities, users):
    entities = types.List(
        filter(
            lambda x: x is not None,
            [
                await types.MessageEntity._parse(client, entity, users)
                for entity in getattr(message, "entities", [])
            ],
        )
    )

    return {
        "text": Str(getattr(message, "text", "")).init(entities) or None,
        "entities": entities or None,
    }


def split_text(text: str, max_length: int = 4096) -> list[str]:
    """Split text into chunks no longer than max_length"""
    if len(text) <= max_length:
        return [text]

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        cut = remaining[:max_length]

        last_newline = cut.rfind("\n")

        if last_newline > 0:
            chunk = cut[:last_newline]
            remaining = remaining[last_newline + 1 :]
        else:
            last_space = cut.rfind(" ")

            if last_space > 0 and last_space > len(cut) // 2:
                chunk = cut[:last_space]
                remaining = remaining[last_space + 1 :]
            else:
                chunk = cut
                remaining = remaining[max_length:]

        if chunk:
            chunks.append(chunk)

    return chunks


def get_first_url(text):
    text = re.sub(r"^\s*(<[\w<>=\s\"]*>)\s*", r"\1", text)
    text = re.sub(r"\s*(</[\w</>]*>)\s*$", r"\1", text)

    matches = re.findall(
        r"(https?):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])", text
    )

    return f"{matches[0][0]}://{matches[0][1]}{matches[0][2]}" if matches else None
