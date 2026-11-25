from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

import pyrogram
from pyrogram import types
from pyrogram.file_id import FileId, FileType
from pyrogram.methods.messages.stream_media import StreamMedia

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

stream_media_module = importlib.import_module("pyrogram.methods.messages.stream_media")


class FakeClient(StreamMedia):
    def __init__(self) -> None:
        self._file_sizes: list[int] = []
        self._closed: bool = False

    @property
    def file_sizes(self) -> list[int]:
        return self._file_sizes

    @property
    def closed(self) -> bool:
        return self._closed

    async def get_file(
        self,
        file_id: FileId,
        file_size: int,
        limit: int,
        offset: int,
        /,
    ) -> AsyncGenerator[bytes]:
        self._file_sizes.append(file_size)

        try:
            yield b"chunk"
        finally:
            self._closed = True


@pytest.mark.asyncio
async def test_stream_media_passes_zero_for_an_unknown_file_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        stream_media_module.FileId,
        "decode",
        lambda _: SimpleNamespace(file_type=FileType.ANIMATION),
    )
    client = FakeClient()
    animation = types.Animation(
        file_id="id",
        file_unique_id="unique",
        width=1,
        height=1,
        duration=1,
    )
    message = types.Message(
        id=1,
        animation=animation,
    )

    chunks = [chunk async for chunk in cast("pyrogram.Client", client).stream_media(message)]

    assert chunks == [b"chunk"]
    assert client.file_sizes == [0]


async def test_closing_the_stream_closes_the_download_at_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        stream_media_module.FileId,
        "decode",
        lambda _: SimpleNamespace(file_type=FileType.DOCUMENT),
    )
    client = FakeClient()
    stream = cast("pyrogram.Client", client).stream_media("id")

    assert await anext(stream) == b"chunk"
    await stream.aclose()

    assert client.closed
