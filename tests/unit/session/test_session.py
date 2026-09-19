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

import asyncio
from hashlib import sha1, sha256
from io import BytesIO
from os import urandom
from typing import TYPE_CHECKING, Final

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.crypto import aes, mtproto
from pyrogram.raw.core import FutureSalt, FutureSalts, Long, Message, TLObject
from pyrogram.session.session import Result, Session, SessionState

if TYPE_CHECKING:
    from concurrent.futures import Executor

_DC_ID: Final[int] = 2
_PORT: Final[int] = 443
_AUTH_KEY: Final[bytes] = bytes(256)
_PACKET: Final[bytes] = b"one packet"

# The salt the session holds before the server offers a new one, and the one it offers.
_STALE_SALT: Final[int] = 111
_NEW_SALT: Final[int] = 999

# The two salts of a pool: the one in use, and the one that takes over from it.
_CURRENT_SALT: Final[int] = 222
_NEXT_SALT: Final[int] = 333

# How long the server gives a salt, and how much of it is left when a test starts.
_SALT_LIFETIME: Final[int] = 30 * 60
_SALT_LEFT: Final[int] = 30

# `bad_server_salt` error code: "incorrect server salt".
#  https://core.telegram.org/mtproto/service_messages_about_messages#notice-of-ignored-error-message
_INCORRECT_SERVER_SALT: Final[int] = 48

# Long enough that a `stop()` which does not wait would have returned several times
#  over, short enough to keep the suite quick.
_NOT_DONE_TIMEOUT: Final[float] = 0.1

# What `Session.STOP_TIMEOUT` is replaced with, so a test of the cancelling path does
#  not sit through the real grace period.
_SHORT_STOP_TIMEOUT: Final[float] = 0.05


class StubProtocol:
    def __init__(self) -> None:
        # `handle_packet` unpacks in this executor; `None` means the loop default one.
        self.crypto_executor: Executor | None = None


class StubConnection:
    def __init__(self) -> None:
        self.closed = asyncio.Event()
        self.packets = [_PACKET]
        self.sent: list[bytes] = []
        self.protocol = StubProtocol()

    async def send(self, payload: bytes) -> None:
        self.sent.append(payload)

    async def recv(self) -> bytes | None:
        if self.packets:
            return self.packets.pop()

        await self.closed.wait()
        return None

    async def close(self) -> None:
        self.closed.set()


def _session() -> Session:
    client = pyrogram.Client("test", api_id=1, api_hash="0" * 32, in_memory=True)

    return Session(client, _DC_ID, "127.0.0.1", _PORT, _AUTH_KEY, test_mode=True)


def _started_session() -> Session:
    session = _session()

    session.connection = StubConnection()
    session._state = SessionState.STARTED
    session.is_started.set()

    return session


def _pack_as_server(message: Message, *, session_id: bytes, auth_key: bytes) -> bytes:
    """`pyrogram.crypto.mtproto.pack`, in the direction the server writes.

    The outer salt is the sender's own and `unpack` skips it, so it is left at zero.
    """
    data: bytes = Long(0) + session_id + message.write()
    padding = urandom(-(len(data) + 12) % 16 + 12)

    # 96 = 88 + 8, the offset an incoming message keys on.
    msg_key = sha256(auth_key[96 : 96 + 32] + data + padding).digest()[8:24]
    aes_key, aes_iv = mtproto.kdf(auth_key, msg_key, False)

    return (
        sha1(auth_key).digest()[-8:] + msg_key + aes.ige256_encrypt(data + padding, aes_key, aes_iv)
    )


async def _server_packet(*, session: Session, body: TLObject) -> bytes:
    """Pack a body into the packet a server would have written"""
    # A server message identity is odd, and the factory allocates client ones.
    message = Message(
        body,
        await session.msg_factory.allocate_message_identity() + 1,
        1,
        len(body),
    )

    return _pack_as_server(
        message,
        session_id=session.session_id,
        auth_key=session.auth_key,
    )


async def _bad_server_salt_packet(*, session: Session, bad_msg_id: int) -> bytes:
    body = raw.types.BadServerSalt(
        bad_msg_id=bad_msg_id,
        bad_msg_seqno=0,
        error_code=_INCORRECT_SERVER_SALT,
        new_server_salt=_NEW_SALT,
    )

    return await _server_packet(
        session=session,
        body=body,
    )


def _last_sent_salt(session: Session) -> int:
    """Read back the salt the session packed its last outgoing message with"""
    connection = session.connection
    assert isinstance(connection, StubConnection)

    # `mtproto.pack` writes `auth_key_id` (8 bytes) and `msg_key` (16), then the
    #  encrypted block, which opens on the salt.
    payload = connection.sent[-1]
    aes_key, aes_iv = mtproto.kdf(session.auth_key, payload[8:24], True)

    return Long.read(BytesIO(aes.ige256_decrypt(payload[24:], aes_key, aes_iv)))


async def _future_salts_packet(
    *,
    session: Session,
    req_msg_id: int,
    salts: list[FutureSalt],
) -> bytes:
    body = FutureSalts(
        req_msg_id=req_msg_id,
        now=int(session.client.server_time),
        salts=salts,
    )

    return await _server_packet(
        session=session,
        body=body,
    )


async def _take_future_salts(*, session: Session, salts: list[FutureSalt]) -> None:
    """Answer the `GetFutureSalts` the session sends, the way the server would"""
    requesting = asyncio.ensure_future(session._update_future_salts())

    while not session.results and not requesting.done():
        await asyncio.sleep(0)

    assert session.results, "the session asked for no future salts"

    await session.handle_packet(
        await _future_salts_packet(
            session=session,
            req_msg_id=next(iter(session.results)),
            salts=salts,
        ),
    )

    await requesting


def _pool_expiring_now(session: Session) -> list[FutureSalt]:
    """A pool of two: a salt with seconds left, and the one that succeeds it"""
    now = int(session.client.server_time)

    return [
        FutureSalt(
            valid_since=now - _SALT_LIFETIME,
            valid_until=now + _SALT_LEFT,
            salt=_CURRENT_SALT,
        ),
        FutureSalt(
            valid_since=now + _SALT_LEFT,
            valid_until=now + _SALT_LEFT + _SALT_LIFETIME,
            salt=_NEXT_SALT,
        ),
    ]


def _recorded_future_salts_requests(session: Session, *, valid_for: int) -> list[TLObject]:
    """Answer every `GetFutureSalts` where it is sent, and collect what was asked"""
    requests: list[TLObject] = []

    async def send(
        data: TLObject,
        *,
        wait_response: bool = True,
        timeout: float = Session.WAIT_TIMEOUT,
    ) -> FutureSalts:
        requests.append(data)

        # The second entry is what keeps the pool from emptying as the first is
        #  promoted, so the threshold is what decides the next request rather than
        #  the pool being empty.
        now = int(session.client.server_time)
        expires_at: int = now + valid_for
        salts = [
            FutureSalt(
                valid_since=now - _SALT_LIFETIME,
                valid_until=expires_at,
                salt=_CURRENT_SALT,
            ),
            FutureSalt(
                valid_since=expires_at,
                valid_until=expires_at + _SALT_LIFETIME,
                salt=_NEXT_SALT,
            ),
        ]

        return FutureSalts(
            req_msg_id=0,
            now=now,
            salts=salts,
        )

    session.send = send

    return requests


async def test_stop_waits_for_the_packet_it_is_still_handling() -> None:
    session = _started_session()

    release = asyncio.Event()
    handled: bool = False

    async def handle_packet(packet: bytes) -> None:
        nonlocal handled

        await release.wait()
        handled = True

    session.handle_packet = handle_packet
    session.recv_task = asyncio.create_task(session.recv_worker())

    await asyncio.sleep(0)

    stopping = asyncio.ensure_future(session.stop())

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(asyncio.shield(stopping), _NOT_DONE_TIMEOUT)

    assert not handled

    release.set()
    await stopping

    assert handled
    assert session.pending_tasks == set()


async def test_stop_cancels_a_packet_that_will_not_finish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Session, "STOP_TIMEOUT", _SHORT_STOP_TIMEOUT)

    session = _started_session()

    async def handle_packet(packet: bytes) -> None:
        await asyncio.Event().wait()

    session.handle_packet = handle_packet
    session.recv_task = asyncio.create_task(session.recv_worker())

    await asyncio.sleep(0)

    handling = next(iter(session.pending_tasks))

    await session.stop()

    assert handling.cancelled()
    assert session.pending_tasks == set()


async def test_a_finished_task_leaves_the_pending_set() -> None:
    session = _started_session()

    task = session._create_tracked_task(asyncio.sleep(0))

    assert session.pending_tasks == {task}

    await task
    await asyncio.sleep(0)

    assert session.pending_tasks == set()


async def test_a_restart_queued_before_stop_does_not_reconnect() -> None:
    session = _started_session()

    started: bool = False

    async def start() -> None:
        nonlocal started

        started = True

    session.start = start

    # The task is only scheduled here: it runs once the loop is yielded to, which is
    #  after the stop below, and that is the order the client shuts down in.
    restarting = asyncio.create_task(session.restart())

    await session.stop()
    await restarting

    assert not started
    assert session.state is SessionState.STOPPED


async def test_a_restart_already_starting_is_stopped_again() -> None:
    session = _started_session()

    starting = asyncio.Event()
    release = asyncio.Event()

    async def start() -> None:
        starting.set()
        await release.wait()

        session._state = SessionState.STARTED
        session.is_started.set()

    session.start = start
    restarting = asyncio.create_task(session.restart())

    await starting.wait()
    await session.stop()

    release.set()
    await restarting

    assert session.state is SessionState.STOPPED
    assert not session.is_started.is_set()


async def test_stop_fails_the_request_still_waiting_for_its_answer() -> None:
    session = _started_session()

    sending = asyncio.ensure_future(session.send(raw.functions.Ping(ping_id=0)))

    while not session.results:
        await asyncio.sleep(0)

    await session.stop()

    with pytest.raises(TimeoutError, match="stopped"):
        await asyncio.wait_for(sending, _NOT_DONE_TIMEOUT)

    assert session.results == {}


async def test_stop_drops_the_acks_owed_to_the_closed_connection() -> None:
    session = _started_session()

    # A server message identity is odd, and its ack was never flushed.
    session.pending_acks.add(await session.msg_factory.allocate_message_identity() + 1)

    await session.stop()

    assert session.pending_acks == set()


async def test_a_bad_server_salt_nobody_awaits_still_updates_the_salt() -> None:
    session = _started_session()
    session.salt = _STALE_SALT

    # `ping_worker` sends with `wait_response=False`, so nothing registers a `Result`.
    ping_msg_id = await session.msg_factory.allocate_message_identity()

    await session.handle_packet(
        await _bad_server_salt_packet(
            session=session,
            bad_msg_id=ping_msg_id,
        ),
    )

    assert ping_msg_id not in session.results
    assert session.salt == _NEW_SALT


async def test_a_bad_server_salt_still_resolves_the_call_that_waits_for_it() -> None:
    session = _started_session()
    session.salt = _STALE_SALT

    awaited_msg_id = await session.msg_factory.allocate_message_identity()
    session.results[awaited_msg_id] = Result()

    await session.handle_packet(
        await _bad_server_salt_packet(
            session=session,
            bad_msg_id=awaited_msg_id,
        ),
    )

    assert session.results[awaited_msg_id].event.is_set()
    assert session.salt == _NEW_SALT


async def test_the_session_packs_with_the_pooled_salt_once_the_current_one_expires() -> None:
    session = _started_session()

    await _take_future_salts(
        session=session,
        salts=_pool_expiring_now(session),
    )

    await session.send(raw.functions.Ping(ping_id=0), wait_response=False)

    assert _last_sent_salt(session) == _CURRENT_SALT

    # Past the first salt's `valid_until`, and nothing has sent a `BadServerSalt`.
    session.client._server_time_offset += _SALT_LEFT + 1

    await session.send(raw.functions.Ping(ping_id=0), wait_response=False)

    assert _last_sent_salt(session) == _NEXT_SALT
    assert session.results == {}


async def test_future_salts_are_not_asked_for_twice_within_the_minute() -> None:
    session = _started_session()

    # A salt already inside the threshold, so the interval is the one thing left
    #  that can stop the second request.
    requests = _recorded_future_salts_requests(session, valid_for=_SALT_LEFT)

    await session._update_future_salts()
    await session._update_future_salts()

    assert len(requests) == 1


async def test_future_salts_are_asked_for_before_the_current_salt_expires() -> None:
    session = _started_session()

    # A salt that outlives the interval below, but not by the whole threshold.
    requests = _recorded_future_salts_requests(
        session,
        valid_for=Session.FUTURE_SALTS_INTERVAL + _SALT_LEFT,
    )

    await session._update_future_salts()

    session.client._server_time_offset += Session.FUTURE_SALTS_INTERVAL + 1

    await session._update_future_salts()

    assert len(requests) == 2
    assert session.salt_valid_until > session.client.server_time


@pytest.mark.parametrize(
    "state",
    [
        pytest.param(SessionState.STOPPED, id="never-started"),
        pytest.param(SessionState.STARTING, id="left-starting-by-a-failed-start"),
    ],
)
async def test_invoke_on_a_session_that_is_not_running_raises(
    state: SessionState,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Short enough to keep the suite quick, and `invoke()` waits it out in full
    #  before it gives up on a session that is not running.
    monkeypatch.setattr(Session, "WAIT_TIMEOUT", 0.05)

    session = _session()
    session._state = state

    with pytest.raises(TimeoutError) as raised:
        await session.invoke(raw.functions.help.GetConfig())

    message = str(raised.value)

    assert 'invoke "help.GetConfig"' in message

    # `Session.__str__` carries the state, so this pins the message on both parameters.
    assert str(session) in message
