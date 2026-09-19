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

from io import BytesIO
from typing import TYPE_CHECKING, BinaryIO, Final, Protocol

import pytest

from pyrogram import Client, raw
from pyrogram.methods.stories.edit_story_media import EditStoryMedia
from pyrogram.methods.stories.send_story import SendStory
from pyrogram.parser import Parser

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from pyrogram._typing import PathType

# Both story senders pick the video branch on `guess_mime_type(file.name) == "video/mp4"`,
#  so the name the fake upload reports is what selects it.
STORY_FILE_NAME: Final[str] = "story.mp4"

UPLOADED_STORY_FILE: Final[raw.types.InputFile] = raw.types.InputFile(
    id=1234567890,
    parts=1,
    name=STORY_FILE_NAME,
    md5_checksum="",
)


class InvokeCalled(Exception):
    """Raised by the fake `invoke` once reached, carrying the built query for inspection."""

    def __init__(self, query: raw.core.TLObject) -> None:
        self.query = query


class FakeClient(SendStory, EditStoryMedia):
    """A client that stops at `invoke`, so the built media is read without a network."""

    mimetypes = Client.mimetypes
    guess_mime_type = Client.guess_mime_type

    def __init__(self) -> None:
        self.parser = Parser(None)

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
        return None if path is None else UPLOADED_STORY_FILE

    async def invoke(
        self,
        query: raw.functions.stories.SendStory | raw.functions.stories.EditStory,
    ) -> None:
        raise InvokeCalled(query)


@pytest.fixture
def story_client() -> FakeClient:
    return FakeClient()


class StoryMediaFactory(Protocol):
    def __call__(self, *, in_memory: bool) -> Path | BytesIO: ...


@pytest.fixture
def story_media(tmp_path: Path) -> StoryMediaFactory:
    """The same `.mp4` as either of the two sources a story sender branches on."""

    def _factory(*, in_memory: bool) -> Path | BytesIO:
        if in_memory:
            document = BytesIO()
            document.name = STORY_FILE_NAME

            return document

        on_disk: Path = tmp_path / STORY_FILE_NAME
        on_disk.write_bytes(b"")

        return on_disk

    return _factory
