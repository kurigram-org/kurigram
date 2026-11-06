from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

import pyrogram
from pyrogram import types
from pyrogram.file_id import FileType
from pyrogram.methods.messages.download_media import DownloadMedia

if TYPE_CHECKING:
    from pathlib import Path

download_media_module = importlib.import_module("pyrogram.methods.messages.download_media")


class FakeClient(DownloadMedia):
    def __init__(self, workdir: Path) -> None:
        self.workdir = workdir
        self.packet: tuple[object, ...] | None = None

    async def handle_download(self, packet: tuple[object, ...]) -> None:
        self.packet = packet

    def guess_extension(self, mime_type: str) -> str:
        return ""

    def rnd_id(self) -> str:
        return "test"

    def captured_packet(self) -> tuple[object, ...]:
        assert self.packet is not None
        return self.packet


@pytest.mark.parametrize(
    ("media_file_name", "expected_file_name"),
    [
        ("../outside.txt", "outside.txt"),
        (r"..\outside.txt", "outside.txt"),
        ("D:outside.txt", "outside.txt"),
    ],
)
@pytest.mark.asyncio
async def test_download_media_sanitizes_telegram_file_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    media_file_name: str,
    expected_file_name: str,
) -> None:
    monkeypatch.setattr(
        download_media_module.FileId,
        "decode",
        lambda _: SimpleNamespace(file_type=FileType.DOCUMENT),
    )
    client = FakeClient(tmp_path)
    media = types.Document(file_id="id", file_unique_id="unique", file_name=media_file_name)

    await cast("pyrogram.Client", client).download_media(media)
    packet = client.captured_packet()

    assert packet[1] == tmp_path / "downloads"
    assert packet[2] == expected_file_name


@pytest.mark.asyncio
async def test_download_media_replaces_dot_path_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        download_media_module.FileId,
        "decode",
        lambda _: SimpleNamespace(file_type=FileType.DOCUMENT),
    )
    client = FakeClient(tmp_path)
    media = types.Document(file_id="id", file_unique_id="unique", file_name="..")

    await cast("pyrogram.Client", client).download_media(media)
    packet = client.captured_packet()

    assert packet[1] == tmp_path / "downloads"
    assert packet[2] not in (".", "..")
