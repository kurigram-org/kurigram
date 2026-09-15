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

from collections.abc import Callable
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Final

import pytest

from pyrogram import Client, raw
from pyrogram._typing import PathType
from pyrogram.methods.messages.send_document import SendDocument
from pyrogram.parser import Parser

_UPLOADED_FILE: Final[raw.types.InputFile] = raw.types.InputFile(
    id=1234567890,
    parts=1,
    name="upload.bin",
    md5_checksum="",
)

# The reporter's case: a `.webp` the server re-reads as a sticker unless `force_file` says
#  otherwise. https://github.com/KurimuzonAkuma/kurigram/issues/180
_FILE_NAME: Final[str] = "sticker.webp"
_CONTENT: Final[bytes] = b"RIFF0000WEBPVP8 "


class FakeClient(SendDocument):
    """A client that records the media built for `messages.SendMedia`, uploading nothing."""

    mimetypes = Client.mimetypes
    guess_mime_type = Client.guess_mime_type

    def __init__(self) -> None:
        self.parser = Parser(None)
        self.captured: raw.base.InputMedia | None = None

    def rnd_id(self) -> int:
        return 1

    async def resolve_peer(self, peer_id: int | str) -> raw.base.InputPeer:
        return raw.types.InputPeerUser(
            user_id=int(peer_id),
            access_hash=0,
        )

    async def save_file(
        self,
        path: PathType | BinaryIO | None,
        file_id: int | None = None,
        file_part: int = 0,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> raw.types.InputFile | None:
        return None if path is None else _UPLOADED_FILE

    async def invoke(
        self,
        query: raw.functions.messages.SendMedia,
        business_connection_id: str | None = None,
    ) -> raw.base.messages.Messages:
        self.captured = query.media

        return raw.types.messages.Messages(
            messages=[],
            chats=[],
            users=[],
            topics=[],
        )


def _in_memory_document() -> BytesIO:
    document = BytesIO(_CONTENT)
    document.name = _FILE_NAME

    return document


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("force_document", "expected_force_file"),
    [
        pytest.param(True, True, id="forced"),
        # `force_file=force_document or None` collapses both falsy values, and the field is
        #  optional in the schema, so an unforced upload must not carry it at all.
        pytest.param(None, None, id="unset"),
        pytest.param(False, None, id="explicitly-off"),
    ],
)
async def test_force_document_reaches_the_media_built_from_a_bytesio(
    *,
    force_document: bool | None,
    expected_force_file: bool | None,
) -> None:
    client = FakeClient()

    await client.send_document(
        chat_id=7,
        document=_in_memory_document(),
        force_document=force_document,
    )

    assert client.captured == raw.types.InputMediaUploadedDocument(
        mime_type="image/webp",
        file=_UPLOADED_FILE,
        force_file=expected_force_file,
        attributes=[raw.types.DocumentAttributeFilename(file_name=_FILE_NAME)],
    )


@pytest.mark.asyncio
async def test_both_branches_build_the_same_media_for_the_same_document(tmp_path: Path) -> None:
    on_disk: Path = tmp_path / _FILE_NAME
    on_disk.write_bytes(_CONTENT)

    from_disk = FakeClient()
    await from_disk.send_document(
        chat_id=7,
        document=on_disk,
        force_document=True,
    )

    from_memory = FakeClient()
    await from_memory.send_document(
        chat_id=7,
        document=_in_memory_document(),
        force_document=True,
    )

    assert from_memory.captured == from_disk.captured
