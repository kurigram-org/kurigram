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

"""What `Client` does without a network: plugin loading and the download path.

`load_plugins()` reads a plugin package without tripping over what else lives in it.
A plugin module is ordinary user code, so anything at all can sit beside the decorated
functions: a database handle, a client object, a lazily built proxy.

`handle_download` and `get_file` run their real chunk loop against a stubbed media
session, so what a progress callback raises provably ends the transfer.
"""

from __future__ import annotations as _annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Final, Protocol

import pytest

from pyrogram import Client, StopTransmission, filters, raw
from pyrogram.client import _plugin_handlers
from pyrogram.file_id import FileId, FileType
from pyrogram.handlers import MessageHandler

if TYPE_CHECKING:
    from concurrent.futures import Executor

_PLUGIN_SOURCE: Final[str] = """
from pyrogram import Client


class AnyAttribute:
    # Answers every attribute with another instance, the way a PyMongo collection does.

    def __getattr__(self, name):
        return AnyAttribute()


collection = AnyAttribute()


@Client.on_message()
async def greet(client, message):
    pass
"""


_KEYWORD_PLUGIN_SOURCE: Final[str] = """
from pyrogram import Client, filters


@Client.on_message(filters=filters.text, group=1)
async def greet(client, message):
    pass
"""

_REFUSED_PLUGIN_SOURCE: Final[str] = """
async def greet(client, message):
    pass


greet.handlers = [("not a handler", 0)]
"""


class PluginWriter(Protocol):
    def __call__(self, package: str, *, source: str) -> str: ...


@pytest.fixture
def write_plugin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> PluginWriter:
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    # Each test needs a package of its own: `import_module` caches by name, so a second
    #  package sharing a name resolves to the first one's files.
    def _write(package: str, *, source: str) -> str:
        root: Path = tmp_path / package
        root.mkdir()
        (root / "handlers.py").write_text(source)

        return package

    return _write


def _plugin_client(root: str) -> Client:
    client = Client(
        name="plugin_probe",
        in_memory=True,
    )
    client.plugins = {"root": root, "enabled": True}

    return client


def test_load_plugins_reads_past_an_attribute_proxy(write_plugin: PluginWriter) -> None:
    client = _plugin_client(write_plugin("proxy_plugins", source=_PLUGIN_SOURCE))

    client.load_plugins()

    registered = [
        handler
        for group in client.dispatcher.groups.values()
        for handler in group
        if isinstance(handler, MessageHandler)
    ]

    assert len(registered) == 1


def test_plugin_handlers_ignores_what_is_not_a_pair_list() -> None:
    class AnyAttribute:
        def __getattr__(self, name: str) -> AnyAttribute:
            return AnyAttribute()

    def undecorated() -> None:
        pass

    def decorated() -> None:
        pass

    decorated.handlers = [(MessageHandler(decorated), 0)]

    assert _plugin_handlers(AnyAttribute()) is None
    assert _plugin_handlers(undecorated) is None
    assert _plugin_handlers(decorated) == decorated.handlers


def test_load_plugins_registers_a_handler_declared_by_keyword(
    write_plugin: PluginWriter,
) -> None:
    client = _plugin_client(write_plugin("keyword_plugins", source=_KEYWORD_PLUGIN_SOURCE))

    client.load_plugins()

    (handler,) = client.dispatcher.groups[1]

    assert isinstance(handler, MessageHandler)
    assert handler.filters is filters.text


def test_load_plugins_reports_the_pair_it_refuses(
    write_plugin: PluginWriter,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _plugin_client(write_plugin("refused_plugins", source=_REFUSED_PLUGIN_SOURCE))

    with caplog.at_level(logging.WARNING, logger="pyrogram.client"):
        client.load_plugins()

    assert client.dispatcher.groups == {}
    assert "greet" in caplog.text


_CHUNK_SIZE: Final[int] = 1024 * 1024

# Three full chunks and a half, so the loop only ends early if something ends it.
_PAYLOAD_SIZE: Final[int] = 3 * _CHUNK_SIZE + _CHUNK_SIZE // 2


class MediaSession:
    """A media session serving one fixed payload in 1 MiB chunks."""

    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    async def invoke(
        self,
        query: raw.functions.upload.GetFile,
        *,
        sleep_threshold: int = 0,
    ) -> raw.types.upload.File:
        chunk = self.payload[query.offset : query.offset + query.limit]

        return raw.types.upload.File(
            type=raw.types.storage.FileUnknown(),
            mtime=0,
            bytes=chunk,
        )


class Downloader:
    """A client cut down to the download path: the real loop over a stubbed network."""

    handle_download = Client.handle_download
    get_file = Client.get_file

    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.get_file_semaphore = asyncio.Semaphore(1)
        self.executor: Executor | None = None

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return asyncio.get_event_loop()

    async def get_session(self, dc_id: int, *, is_media: bool = False) -> MediaSession:
        return MediaSession(self.payload)


def _document_file_id() -> FileId:
    return FileId(
        file_type=FileType.DOCUMENT,
        dc_id=2,
        media_id=1,
        access_hash=1,
        file_reference=b"ref",
    )


async def test_a_download_reports_progress_in_bytes_and_lands_on_disk(tmp_path: Path) -> None:
    payload: bytes = b"x" * _PAYLOAD_SIZE
    reported: list[int] = []

    async def progress(current: int, total: int) -> None:
        reported.append(current)

    packet = (_document_file_id(), str(tmp_path), "whole.bin", False, _PAYLOAD_SIZE, progress, ())

    file_path = await Downloader(payload).handle_download(packet)

    assert file_path is not None
    assert Path(file_path).read_bytes() == payload
    assert reported == [_CHUNK_SIZE, 2 * _CHUNK_SIZE, 3 * _CHUNK_SIZE, _PAYLOAD_SIZE]


@pytest.mark.parametrize(
    "asynchronous",
    [
        pytest.param(True, id="async-callback"),
        pytest.param(False, id="sync-callback-via-executor"),
    ],
)
async def test_stop_transmission_from_a_progress_callback_ends_a_download(
    tmp_path: Path,
    *,
    asynchronous: bool,
) -> None:
    calls: list[int] = []

    def cancel_on_second_chunk(current: int, total: int) -> None:
        calls.append(current)

        if len(calls) == 2:
            raise StopTransmission

    async def asynchronous_cancel(current: int, total: int) -> None:
        cancel_on_second_chunk(current, total)

    progress = asynchronous_cancel if asynchronous else cancel_on_second_chunk
    packet = (_document_file_id(), str(tmp_path), "stopped.bin", False, _PAYLOAD_SIZE, progress, ())

    result = await Downloader(b"x" * _PAYLOAD_SIZE).handle_download(packet)

    assert result is None
    assert calls == [_CHUNK_SIZE, 2 * _CHUNK_SIZE]

    # The `.temp` file is deleted with the abort, so nothing at all is left behind.
    assert list(tmp_path.iterdir()) == []
