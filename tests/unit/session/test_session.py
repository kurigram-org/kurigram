#  Kurigram - Telegram MTProto API Client Library for Python
#
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2024-present KurimuzonAkuma <https://github.com/KurimuzonAkuma>
#
#  This file is part of Kurigram.
#
#  Kurigram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Kurigram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Kurigram. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations

import asyncio
import time
from hashlib import sha1, sha256
from io import BytesIO
from os import urandom
from typing import TYPE_CHECKING, Final

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.errors import BadMsgNotification
from pyrogram.crypto import aes, mtproto
from pyrogram.raw.core import FutureSalt, FutureSalts, Long, Message, MsgContainer, TLObject
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

# `bad_msg_notification` error codes: `msg_id` too low or too high and `msg_seqno` too
#  low or too high, which a re-send with a new identity recovers, and "incorrect two
#  lower order `msg_id` bits", a client bug no re-send can fix.
#  https://core.telegram.org/mtproto/service_messages_about_messages#notice-of-ignored-error-message
_MSG_ID_TOO_LOW: Final[int] = 16
_MSG_ID_TOO_HIGH: Final[int] = 17
_MSG_ID_NOT_DIVISIBLE_BY_FOUR: Final[int] = 18
_MSG_SEQNO_TOO_LOW: Final[int] = 32
_MSG_SEQNO_TOO_HIGH: Final[int] = 33

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

    async def connect(self) -> None:
        pass

    async def send(self, payload: bytes) -> None:
        self.sent.append(payload)

    async def recv(self) -> bytes | None:
        if self.packets:
            return self.packets.pop()

        await self.closed.wait()
        return None

    async def close(self) -> None:
        self.closed.set()


class AnsweringConnection(StubConnection):
    """Answers every awaited request with the next of `answers`, as the server would"""

    def __init__(self, *, session: Session, answers: list[TLObject]) -> None:
        super().__init__()

        self._session = session
        self._answers = answers

    async def send(self, payload: bytes) -> None:
        await super().send(payload)

        for result in self._session.results.values():
            result.value = self._answers.pop(0)
            result.event.set()


def _bad_msg_notification(*, error_code: int) -> raw.types.BadMsgNotification:
    return raw.types.BadMsgNotification(
        bad_msg_id=0,
        bad_msg_seqno=0,
        error_code=error_code,
    )


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


@pytest.mark.parametrize(
    "worker",
    [
        pytest.param("ping_task", id="ping"),
        pytest.param("recv_task", id="recv"),
    ],
)
async def test_a_restart_gets_past_a_worker_that_died(worker: str) -> None:
    session = _started_session()

    async def die() -> None:
        raise AttributeError("'BadMsgNotification' object has no attribute 'salts'")

    setattr(session, worker, asyncio.create_task(die()))
    await asyncio.sleep(0)

    started: bool = False

    async def start() -> None:
        nonlocal started

        started = True

    session.start = start

    # Before: `restart()` raised the worker's `AttributeError` and the session stayed
    #  `STOPPING`, so every later `invoke` failed after `WAIT_TIMEOUT`.
    await session.restart()

    assert started
    assert getattr(session, worker) is None


async def test_stop_fails_the_request_still_waiting_for_its_answer() -> None:
    session = _started_session()

    sending = asyncio.ensure_future(session.send(raw.functions.Ping(ping_id=0)))

    while not session.results:
        await asyncio.sleep(0)

    await session.stop()

    with pytest.raises(TimeoutError, match="stopped"):
        await asyncio.wait_for(sending, _NOT_DONE_TIMEOUT)

    assert session.results == {}


async def test_a_cancelled_request_leaves_no_waiter_behind() -> None:
    session = _started_session()

    sending = asyncio.ensure_future(session.send(raw.functions.Ping(ping_id=0)))

    while not session.results:
        await asyncio.sleep(0)

    sending.cancel()
    await asyncio.gather(sending, return_exceptions=True)

    assert session.results == {}


async def test_a_restart_keeps_the_acks_the_session_still_owes() -> None:
    session = _started_session()

    # A server message identity is odd, and its ack was never flushed.
    unacked_msg_id: int = await session.msg_factory.allocate_message_identity() + 1
    session.pending_acks.add(unacked_msg_id)

    # The half of `restart()` that runs before it reconnects.
    await session._stop()

    assert session.pending_acks == {unacked_msg_id}


async def test_a_rejected_message_does_not_drop_the_rest_of_its_container() -> None:
    session = _started_session()

    ping_msg_id = await session.msg_factory.allocate_message_identity()
    session.results[ping_msg_id] = Result()

    # Server identities are odd: 1 modulo 4 for an answer, 3 for anything else. The
    #  re-sent message keeps its older identity, which is below the one stored first.
    base_msg_id = await session.msg_factory.allocate_message_identity()
    resent_msg_id: int = base_msg_id + 3
    new_session_msg_id: int = base_msg_id + 7
    pong_msg_id: int = base_msg_id + 9
    container_msg_id: int = base_msg_id + 13

    new_session_created = raw.types.NewSessionCreated(
        first_msg_id=ping_msg_id,
        unique_id=0,
        server_salt=0,
    )
    resent_update = raw.types.UpdatesTooLong()
    pong = raw.types.Pong(
        msg_id=ping_msg_id,
        ping_id=0,
    )
    container = MsgContainer(
        [
            Message(new_session_created, new_session_msg_id, 2, len(new_session_created)),
            Message(resent_update, resent_msg_id, 3, len(resent_update)),
            Message(pong, pong_msg_id, 4, len(pong)),
        ],
    )

    await session.handle_packet(
        _pack_as_server(
            Message(container, container_msg_id, 4, len(container)),
            session_id=session.session_id,
            auth_key=session.auth_key,
        ),
    )

    # Was "Restarting session due to - TimeoutError - Request timed out" from `start()`.
    assert session.results[ping_msg_id].event.is_set()
    assert session.stored_msg_ids == [new_session_msg_id, pong_msg_id]


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


async def test_a_bad_msg_notification_answer_is_raised_not_returned() -> None:
    session = _started_session()
    session.connection = AnsweringConnection(
        session=session,
        answers=[_bad_msg_notification(error_code=_MSG_ID_TOO_LOW)],
    )

    # Returned, it reached callers as their result: `_update_future_salts()` read
    #  `.salts` off it and the `AttributeError` killed the ping task.
    with pytest.raises(BadMsgNotification) as raised:
        await session.send(raw.functions.Ping(ping_id=0))

    assert raised.value.code == _MSG_ID_TOO_LOW


@pytest.mark.parametrize(
    "error_code",
    [
        pytest.param(_MSG_ID_TOO_LOW, id="msg-id-too-low"),
        pytest.param(_MSG_ID_TOO_HIGH, id="msg-id-too-high"),
        pytest.param(_MSG_SEQNO_TOO_LOW, id="msg-seqno-too-low"),
        pytest.param(_MSG_SEQNO_TOO_HIGH, id="msg-seqno-too-high"),
    ],
)
async def test_invoke_resends_a_request_the_server_rejected_for_its_identity(
    error_code: int,
) -> None:
    session = _started_session()
    pong = raw.types.Pong(
        msg_id=0,
        ping_id=0,
    )
    session.connection = AnsweringConnection(
        session=session,
        answers=[_bad_msg_notification(error_code=error_code), pong],
    )

    result = await session.invoke(
        raw.functions.Ping(ping_id=0),
        retry_delay=0,
    )

    assert result == pong


async def test_invoke_waits_for_the_session_to_reconnect_before_retrying(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _started_session()
    waiting_for_reconnect = asyncio.Event()
    wait_until_started = session.is_started.wait
    sent = 0
    pong = raw.types.Pong(msg_id=0, ping_id=0)

    async def send(query, *, timeout):
        nonlocal sent
        assert session.is_started.is_set()
        sent += 1
        if sent == 1:
            session.is_started.clear()
            raise TimeoutError("Session stopped before an answer arrived")
        return pong

    async def wait():
        if not session.is_started.is_set():
            waiting_for_reconnect.set()
        await wait_until_started()

    monkeypatch.setattr(session.is_started, "wait", wait)
    monkeypatch.setattr(session, "send", send)
    request = asyncio.create_task(session.invoke(raw.functions.Ping(ping_id=0), retry_delay=0))
    try:
        await asyncio.wait_for(waiting_for_reconnect.wait(), timeout=1)
        assert not request.done()
        session.is_started.set()
        assert await asyncio.wait_for(request, timeout=1) == pong
    finally:
        request.cancel()
        await asyncio.gather(request, return_exceptions=True)

    assert sent == 2


async def test_invoke_raises_a_bad_msg_notification_no_resend_can_fix() -> None:
    session = _started_session()
    connection = AnsweringConnection(
        session=session,
        answers=[_bad_msg_notification(error_code=_MSG_ID_NOT_DIVISIBLE_BY_FOUR)],
    )
    session.connection = connection

    with pytest.raises(BadMsgNotification):
        await session.invoke(
            raw.functions.Ping(ping_id=0),
            retry_delay=0,
        )

    assert len(connection.sent) == 1


def _start_answered_with(*, session: Session, error_code: int) -> asyncio.Event:
    """Make `start()` connect to a server that answers its `Ping` with this notification"""
    connection = AnsweringConnection(
        session=session,
        answers=[_bad_msg_notification(error_code=error_code)],
    )
    connection.packets = []
    session.client.connection_factory = lambda **_: connection

    restarted = asyncio.Event()

    async def restart() -> None:
        restarted.set()

    session.restart = restart

    return restarted


async def test_start_answered_with_a_resendable_bad_msg_notification_restarts() -> None:
    session = _session()
    restarted = _start_answered_with(
        session=session,
        error_code=_MSG_ID_TOO_LOW,
    )

    # Was `BadMsgNotification: [16] The msg_id is too low` out of `start()`, with the
    #  session stopped, so a restart after a clock jump killed it for good.
    await session.start()
    await asyncio.wait_for(restarted.wait(), _NOT_DONE_TIMEOUT)

    assert session.state is SessionState.STARTING


async def test_start_answered_with_a_bad_msg_notification_no_resend_can_fix_stops() -> None:
    session = _session()
    restarted = _start_answered_with(
        session=session,
        error_code=_MSG_ID_NOT_DIVISIBLE_BY_FOUR,
    )

    with pytest.raises(BadMsgNotification):
        await session.start()

    assert session.state is SessionState.STOPPED
    assert not restarted.is_set()


@pytest.mark.parametrize(
    ("error_code", "clock_offset"),
    [
        pytest.param(_MSG_ID_TOO_LOW, -_SALT_LIFETIME, id="clock-behind"),
        pytest.param(_MSG_ID_TOO_HIGH, _SALT_LIFETIME, id="clock-ahead"),
    ],
)
async def test_a_clock_bad_msg_notification_syncs_the_time_after_the_first_message(
    *,
    error_code: int,
    clock_offset: int,
) -> None:
    session = _started_session()
    packet = await _server_packet(
        session=session,
        body=_bad_msg_notification(error_code=error_code),
    )

    # A clock this far off is what makes the server answer this code.
    session.client._server_time_offset = clock_offset

    await session.handle_packet(packet)

    assert abs(session.client._server_time_offset) < _SALT_LEFT


async def test_the_resend_after_a_msg_id_too_high_follows_the_corrected_clock() -> None:
    session = _started_session()
    packet = await _server_packet(
        session=session,
        body=_bad_msg_notification(error_code=_MSG_ID_TOO_HIGH),
    )

    session.client._server_time_offset = _SALT_LIFETIME
    await session.msg_factory.allocate_message_identity()

    await session.handle_packet(packet)

    resent_msg_id = await session.msg_factory.allocate_message_identity()

    # Was 1800 seconds ahead: the factory went on from the rejected `msg_id`.
    assert resent_msg_id / 2**32 - time.time() < _SALT_LEFT


async def test_the_ping_task_outlives_a_bad_msg_notification_for_its_future_salts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Above zero: at zero `asyncio.wait_for` cancels `Event.wait()` before it runs and
    #  raises `TimeoutError` on a set event too, so the worker never sees the stop below.
    #  https://github.com/python/cpython/blob/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/Lib/asyncio/tasks.py#L475-L485
    monkeypatch.setattr(Session, "PING_INTERVAL", _SHORT_STOP_TIMEOUT / 10)

    session = _started_session()
    attempts: int = 0
    retried = asyncio.Event()

    async def update_future_salts() -> None:
        nonlocal attempts

        attempts += 1

        if attempts > 1:
            retried.set()

        raise BadMsgNotification(_MSG_ID_TOO_LOW)

    session._update_future_salts = update_future_salts
    ping_task = asyncio.create_task(session.ping_worker())

    await asyncio.wait_for(retried.wait(), _NOT_DONE_TIMEOUT)

    assert not ping_task.done()

    session.ping_task_event.set()
    await ping_task
