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

"""Registering a handler takes effect where it is called, whatever is running.

`add_handler` and `remove_handler` are ordinary synchronous methods, so the caller
decides when they happen. They used to schedule the work on a loop instead, which lost
every handler registered before the application started one. Being synchronous, they are
also called from whatever thread the caller is on, which is what the last test here covers.
"""

from __future__ import annotations as _annotations

import asyncio
import sys
import threading
from typing import TYPE_CHECKING, Any, Final, Protocol

import pytest

from pyrogram import Client, raw
from pyrogram.handlers import (
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    ChatMemberUpdatedHandler,
    ChosenInlineResultHandler,
    DeletedMessagesHandler,
    InlineQueryHandler,
    MessageHandler,
    MessageReactionCountHandler,
    MessageReactionHandler,
    PollHandler,
    PreCheckoutQueryHandler,
    RawUpdateHandler,
    ShippingQueryHandler,
    StartHandler,
    StoryHandler,
)
from pyrogram.storage import UpdateState

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterator

    from pyrogram.handlers.handler import Handler
    from pyrogram.types import Message

_REGISTERING_THREADS: Final[int] = 2
_HANDLERS_PER_THREAD: Final[int] = 500
_UPDATES_SENT: Final[int] = 3

# `UpdateShort` reaches the queue without touching storage, and no parser claims the
#  inner update, so a worker hands it to a raw handler untouched.
_UNPARSED_UPDATE: Final[raw.types.UpdateShort] = raw.types.UpdateShort(
    update=raw.types.UpdateDcOptions(dc_options=[]),
    date=0,
)

_GROUP_ID: Final[int] = 7
_EMPTY_ID: Final[int] = 8
_SENDER_ID: Final[int] = 9
_RECIPIENT_ID: Final[int] = 10

_GROUP: Final[raw.types.Chat] = raw.types.Chat(
    id=_GROUP_ID,
    title="Group",
    photo=raw.types.ChatPhotoEmpty(),
    participants_count=2,
    date=1,
    version=1,
)


# The dispatcher calls a handler callback positionally.
async def greet(client: Client, message: Message, /) -> None:
    pass


@pytest.fixture
def client() -> Client:
    return Client(
        name="dispatcher_probe",
        in_memory=True,
    )


@pytest.fixture
def client_without_updates() -> Client:
    """`no_updates` keeps `Dispatcher.start()` off the network: no workers, no gap recovery."""
    return Client(
        name="dispatcher_probe",
        in_memory=True,
        no_updates=True,
    )


def test_a_handler_registered_outside_a_loop_survives_into_one(client: Client) -> None:
    handler = MessageHandler(greet)

    client.add_handler(handler)

    async def registered() -> dict[int, list[Handler[Any]]]:
        return client.dispatcher.groups

    assert asyncio.run(registered()) == {0: [handler]}


def test_groups_are_dispatched_lowest_first(client: Client) -> None:
    last = MessageHandler(greet)
    first = MessageHandler(greet)

    client.add_handler(last, group=3)
    client.add_handler(first, group=-1)

    assert list(client.dispatcher.groups) == [-1, 3]


def _recording_handler(group: int, *, fired: list[int]) -> RawUpdateHandler:
    """A raw handler that notes the group it was registered in, once it runs."""

    async def record(
        client: Client,
        update: raw.base.Update,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        /,
    ) -> None:
        fired.append(group)

    return RawUpdateHandler(record)


async def test_a_lower_group_is_dispatched_before_a_higher_one(client: Client) -> None:
    """What the sort in `add_handler` is for, read off a dispatch rather than off the keys."""
    fired: list[int] = []

    client.add_handler(_recording_handler(3, fired=fired), group=3)
    client.add_handler(_recording_handler(-1, fired=fired), group=-1)

    dispatcher = client.dispatcher

    # An update no parser claims, so the worker reaches the handlers with it untouched and
    #  needs neither the network nor a session.
    dispatcher.updates_queue.put_nowait((raw.types.UpdateDcOptions(dc_options=[]), {}, {}))
    dispatcher.updates_queue.put_nowait(None)

    await dispatcher.handler_worker()

    assert fired == [-1, 3]


def test_remove_handler_takes_the_group_with_its_last_handler(client: Client) -> None:
    handler = MessageHandler(greet)

    client.add_handler(handler, group=2)
    client.remove_handler(handler, group=2)

    assert client.dispatcher.groups == {}


def test_remove_handler_reports_a_group_that_was_never_added(client: Client) -> None:
    with pytest.raises(ValueError, match="Group 7 does not exist"):
        client.remove_handler(MessageHandler(greet), group=7)


def test_registering_leaves_a_mapping_already_being_read_alone(client: Client) -> None:
    dispatching = MessageHandler(greet)
    client.add_handler(dispatching)

    # What a worker mid-update holds: rebuilding the mapping under it must not be seen
    #  by this iteration, nor raise `RuntimeError: dictionary changed size during iteration`.
    groups = iter(client.dispatcher.groups.values())
    handlers = next(groups)

    client.add_handler(MessageHandler(greet), group=1)
    client.add_handler(MessageHandler(greet))

    assert list(groups) == []
    assert handlers == [dispatching]


async def test_start_rebuilds_the_queue_for_the_loop_about_to_read_it(
    client_without_updates: Client,
) -> None:
    dispatcher = client_without_updates.dispatcher
    built_by_the_constructor = dispatcher.updates_queue

    await dispatcher.start()

    assert dispatcher.updates_queue is not built_by_the_constructor


async def test_an_update_is_dropped_while_no_worker_runs(client: Client) -> None:
    """A client that only called `connect()`: nothing drains the queue, so nothing enters it."""
    for _ in range(_UPDATES_SENT):
        await client.handle_updates(_UNPARSED_UPDATE)

    assert client.dispatcher.updates_queue.qsize() == 0


async def test_a_started_dispatcher_delivers_every_update(client: Client) -> None:
    fired: list[int] = []
    client.add_handler(_recording_handler(0, fired=fired))

    await client.dispatcher.start()

    for _ in range(_UPDATES_SENT):
        await client.handle_updates(_UNPARSED_UPDATE)

    await client.dispatcher.stop()

    assert fired == [0] * _UPDATES_SENT


async def test_an_update_after_stop_is_dropped(client: Client) -> None:
    await client.dispatcher.start()
    await client.dispatcher.stop(clear_handlers=False)

    await client.handle_updates(_UNPARSED_UPDATE)

    assert client.dispatcher.updates_queue.qsize() == 0


async def test_an_update_during_the_start_callback_is_delivered(client: Client) -> None:
    """The network delivers while `start_handler` runs; the workers start only after it."""
    fired: list[int] = []
    client.add_handler(_recording_handler(0, fired=fired))

    async def receive(client: Client, /) -> None:
        await client.handle_updates(_UNPARSED_UPDATE)

    client.add_handler(StartHandler(receive))

    await client.dispatcher.start()
    await client.dispatcher.stop()

    assert fired == [0]


async def test_an_update_while_stop_is_pending_is_dropped(client: Client) -> None:
    handling = asyncio.Event()
    released = asyncio.Event()

    async def hold(
        client: Client,
        update: raw.base.Update,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        /,
    ) -> None:
        handling.set()
        await released.wait()

    client.add_handler(RawUpdateHandler(hold))

    await client.dispatcher.start()
    await client.handle_updates(_UNPARSED_UPDATE)
    await handling.wait()

    # One yield lets `stop()` queue its sentinels while every worker is still busy.
    stopping = asyncio.create_task(client.dispatcher.stop(clear_handlers=False))
    await asyncio.sleep(0)

    await client.handle_updates(_UNPARSED_UPDATE)
    released.set()
    await stopping

    assert client.dispatcher.updates_queue.qsize() == 0


async def test_a_restart_keeping_handlers_runs_only_the_new_workers(client: Client) -> None:
    fired: list[int] = []
    client.add_handler(_recording_handler(0, fired=fired))

    await client.dispatcher.start()
    await client.dispatcher.stop(clear_handlers=False)

    assert client.dispatcher.handler_worker_tasks == []

    await client.dispatcher.start()
    await client.handle_updates(_UNPARSED_UPDATE)
    await client.dispatcher.stop(clear_handlers=False)

    assert client.dispatcher.handler_worker_tasks == []
    assert fired == [0]


async def test_a_started_client_without_updates_queues_nothing(
    client_without_updates: Client,
) -> None:
    """`start()` spawns no worker under `no_updates`, so admission stays closed."""
    await client_without_updates.dispatcher.start()

    await client_without_updates.handle_updates(_UNPARSED_UPDATE)

    assert client_without_updates.dispatcher.updates_queue.qsize() == 0


class _Route(Protocol):
    """Feeds the client one way an update reaches `Dispatcher.enqueue()`."""

    async def __call__(self, client: Client, /) -> None: ...


# Answers every `GetDifference` with one message and one other update, so a route
#  through a difference reaches both of its `enqueue()` calls.
_DIFFERENCE: Final[raw.types.updates.Difference] = raw.types.updates.Difference(
    new_messages=[raw.types.MessageEmpty(id=1)],
    new_encrypted_messages=[],
    other_updates=[raw.types.UpdateDcOptions(dc_options=[])],
    chats=[],
    users=[],
    state=raw.types.updates.State(
        pts=2,
        qts=0,
        date=1,
        seq=1,
        unread_count=0,
    ),
)


async def _answer_with_difference(query: raw.core.TLObject, /) -> raw.types.updates.Difference:
    return _DIFFERENCE


async def _send_updates_container(client: Client, /) -> None:
    updates = raw.types.Updates(
        updates=[raw.types.UpdateDcOptions(dc_options=[])],
        users=[],
        chats=[],
        date=1,
        seq=1,
    )
    await client.handle_updates(updates)


async def _send_short_message(client: Client, /) -> None:
    short_message = raw.types.UpdateShortMessage(
        id=1,
        user_id=1,
        message="",
        pts=2,
        pts_count=1,
        date=1,
    )
    await client.handle_updates(short_message)


async def _recover_a_gap(client: Client, /) -> None:
    await client.storage.set_update_state(UpdateState(0, 1, None, 1, 1))
    await client.recover_gaps()


_ROUTES: Final[tuple[Any, ...]] = (
    pytest.param(_send_updates_container, ["UpdateDcOptions"], id="updates-container"),
    pytest.param(
        _send_short_message,
        ["UpdateDcOptions", "UpdateNewMessage"],
        id="short-message-difference",
    ),
    pytest.param(
        _recover_a_gap,
        ["UpdateDcOptions", "UpdateNewMessage"],
        id="recovered-difference",
    ),
)


@pytest.fixture
async def client_with_storage(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[Client]:
    """Peers and update states are written on every route, and `invoke` stays offline."""
    monkeypatch.setattr(client, "invoke", _answer_with_difference)
    await client.storage.open()

    yield client

    await client.storage.close()


@pytest.mark.parametrize(("route", "delivered"), _ROUTES)
async def test_every_route_drops_while_no_worker_runs(
    client_with_storage: Client,
    route: _Route,
    delivered: list[str],
) -> None:
    await route(client_with_storage)

    assert client_with_storage.dispatcher.updates_queue.qsize() == 0


@pytest.mark.parametrize(("route", "delivered"), _ROUTES)
async def test_every_route_delivers_once_started(
    client_with_storage: Client,
    route: _Route,
    delivered: list[str],
) -> None:
    received: list[str] = []

    async def record(
        client: Client,
        update: raw.base.Update,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        /,
    ) -> None:
        received.append(type(update).__name__)

    client_with_storage.add_handler(RawUpdateHandler(record))

    await client_with_storage.dispatcher.start()
    await route(client_with_storage)
    await client_with_storage.dispatcher.stop()

    assert sorted(received) == delivered


def _updates_with_an_empty_entity(kind: str) -> raw.types.Updates:
    """A group message reading the empty entity Telegram listed beside it in the update."""
    if kind == "user":
        # A TON wallet transfer reads its `sender` from `users` by the sender's id.
        message: raw.base.Message = raw.types.MessageService(
            id=1,
            peer_id=raw.types.PeerChat(chat_id=_GROUP_ID),
            from_id=raw.types.PeerUser(user_id=_EMPTY_ID),
            date=1,
            action=raw.types.MessageActionGramTransfer(
                transaction_id="transaction",
                peer_address="address",
                amount=1,
            ),
        )
        users: list[raw.base.User] = [raw.types.UserEmpty(id=_EMPTY_ID)]
        chats: list[raw.base.Chat] = [_GROUP]
    else:
        # `guest_bot_caller_chat` reads `chats` by the id of `guestchat_via_from`.
        message = raw.types.Message(
            id=1,
            peer_id=raw.types.PeerChat(chat_id=_GROUP_ID),
            from_id=raw.types.PeerUser(user_id=_SENDER_ID),
            guestchat_via_from=raw.types.PeerChat(chat_id=_EMPTY_ID),
            date=1,
            message="text",
            # What `Message.read` gives for an absent flag, and what the parser iterates.
            restriction_reason=[],
        )
        users = [
            raw.types.User(
                id=_SENDER_ID,
                first_name="Sender",
                access_hash=0,
            ),
        ]
        chats = [_GROUP, raw.types.ChatEmpty(id=_EMPTY_ID)]

    update = raw.types.UpdateNewMessage(
        message=message,
        pts=2,
        pts_count=1,
    )

    return raw.types.Updates(
        updates=[update],
        users=users,
        chats=chats,
        date=1,
        seq=1,
    )


@pytest.mark.parametrize(
    "kind",
    [
        pytest.param("user", id="user-empty"),
        pytest.param("chat", id="chat-empty"),
    ],
)
async def test_an_empty_entity_in_an_update_reaches_parsers_as_a_missing_one(
    client_with_storage: Client,
    kind: str,
) -> None:
    # The strict parsers raise on `userEmpty` and `chatEmpty`, which dropped the whole
    #  update, raw handlers included; on `main` the field was `None`.
    messages: list[Message] = []
    raw_entities: list[str] = []

    async def record_message(client: Client, message: Message, /) -> None:
        messages.append(message)

    async def record_raw(
        client: Client,
        update: raw.base.Update,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        /,
    ) -> None:
        raw_entities.extend(type(entity).__name__ for entity in [*users.values(), *chats.values()])

    client_with_storage.add_handler(MessageHandler(record_message), group=0)
    client_with_storage.add_handler(RawUpdateHandler(record_raw), group=1)

    await client_with_storage.dispatcher.start()
    await client_with_storage.handle_updates(_updates_with_an_empty_entity(kind))
    await client_with_storage.dispatcher.stop()

    [message] = messages
    empty_field = (
        message.ton_wallet_transfer.sender if kind == "user" else message.guest_bot_caller_chat
    )
    empty_name = "UserEmpty" if kind == "user" else "ChatEmpty"

    assert (message.chat.id, empty_field, empty_name in raw_entities) == (-_GROUP_ID, None, True)


@pytest.mark.parametrize(
    "listed",
    [
        pytest.param([], id="no-empty-entity"),
        pytest.param([raw.types.UserEmpty(id=_EMPTY_ID)], id="user-empty"),
        # The parser takes the listed sender as missing and fetches it, so raw handlers get
        #  the fetched user, the one the parsed message names, in place of `userEmpty`.
        pytest.param([raw.types.UserEmpty(id=_SENDER_ID)], id="sender-user-empty"),
    ],
)
async def test_a_user_a_parser_fetches_reaches_raw_handlers(
    client_with_storage: Client,
    monkeypatch: pytest.MonkeyPatch,
    listed: list[raw.base.User],
) -> None:
    # A private message parser fetches a sender missing from the update and replaces the
    #  listed recipient with the fetched one, in a copy of `users` without the empty
    #  entries, so raw handlers see both only if the copy is merged back.
    recipient = raw.types.User(
        id=_RECIPIENT_ID,
        first_name="Recipient",
        access_hash=0,
    )
    fetched_recipient = raw.types.User(
        id=_RECIPIENT_ID,
        first_name="Fetched recipient",
        access_hash=0,
    )
    sender = raw.types.User(
        id=_SENDER_ID,
        first_name="Sender",
        access_hash=0,
    )

    async def resolve_peer(peer_id: int) -> raw.types.InputPeerUser:
        return raw.types.InputPeerUser(
            user_id=peer_id,
            access_hash=0,
        )

    async def invoke(query: raw.functions.users.GetUsers) -> list[raw.base.User]:
        return [sender, fetched_recipient]

    monkeypatch.setattr(client_with_storage, "resolve_peer", resolve_peer)
    monkeypatch.setattr(client_with_storage, "invoke", invoke)

    raw_users: dict[int, raw.base.User] = {}

    async def record_raw(
        client: Client,
        update: raw.base.Update,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        /,
    ) -> None:
        raw_users.update(users)

    client_with_storage.add_handler(RawUpdateHandler(record_raw))

    await client_with_storage.dispatcher.start()
    await client_with_storage.handle_updates(
        raw.types.Updates(
            updates=[
                raw.types.UpdateNewMessage(
                    message=raw.types.Message(
                        id=1,
                        peer_id=raw.types.PeerUser(user_id=_RECIPIENT_ID),
                        from_id=raw.types.PeerUser(user_id=_SENDER_ID),
                        date=1,
                        message="text",
                        restriction_reason=[],
                    ),
                    pts=2,
                    pts_count=1,
                ),
            ],
            users=[recipient, *listed],
            chats=[],
            date=1,
            seq=1,
        ),
    )
    await client_with_storage.dispatcher.stop()

    assert (raw_users[_SENDER_ID], raw_users[_RECIPIENT_ID]) == (sender, fetched_recipient)


async def test_a_channel_a_parser_fetches_reaches_raw_handlers(
    client_with_storage: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A story parser fetches a channel missing from the update into the dict it reads,
    #  which is a copy, so raw handlers see the channel only if it is copied back.
    channel = raw.types.Channel(
        id=_GROUP_ID,
        title="Channel",
        photo=raw.types.ChatPhotoEmpty(),
        date=1,
        access_hash=0,
        # What `Channel.read` gives for absent flags, and what the parser iterates.
        usernames=[],
        restriction_reason=[],
    )

    async def invoke(query: raw.functions.channels.GetChannels) -> raw.types.messages.Chats:
        return raw.types.messages.Chats(chats=[channel])

    monkeypatch.setattr(client_with_storage, "invoke", invoke)

    raw_chats: dict[int, raw.base.Chat] = {}

    async def record_raw(
        client: Client,
        update: raw.base.Update,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        /,
    ) -> None:
        raw_chats.update(chats)

    client_with_storage.add_handler(RawUpdateHandler(record_raw))

    await client_with_storage.dispatcher.start()
    await client_with_storage.handle_updates(
        raw.types.Updates(
            updates=[
                raw.types.UpdateStory(
                    peer=raw.types.PeerChannel(channel_id=_GROUP_ID),
                    story=raw.types.StoryItemDeleted(id=1),
                ),
            ],
            users=[],
            chats=[],
            date=1,
            seq=1,
        ),
    )
    await client_with_storage.dispatcher.stop()

    assert raw_chats == {_GROUP_ID: channel}


def _service_from(action: raw.base.MessageAction, *, sender_id: int) -> raw.types.UpdateNewMessage:
    """A basic group service message, the shape every join, leave and invite action takes."""
    return raw.types.UpdateNewMessage(
        message=raw.types.MessageService(
            id=1,
            peer_id=raw.types.PeerChat(chat_id=_GROUP_ID),
            from_id=raw.types.PeerUser(user_id=sender_id),
            date=1,
            action=action,
        ),
        pts=2,
        pts_count=1,
    )


# Each update names the user or basic group Telegram lists as `userEmpty` or `chatEmpty`,
#  and the field reading it by id.
_UPDATES_NAMING_AN_EMPTY_ENTITY: Final[tuple[Any, ...]] = (
    pytest.param(
        raw.types.UpdateInlineBotCallbackQuery(
            query_id=1,
            user_id=_EMPTY_ID,
            msg_id=raw.types.InputBotInlineMessageID(
                dc_id=1,
                id=1,
                access_hash=1,
            ),
            chat_instance=1,
        ),
        CallbackQueryHandler,
        "from_user",
        None,
        id="callback-query",
    ),
    pytest.param(
        raw.types.UpdateBotInlineQuery(
            query_id=1,
            user_id=_EMPTY_ID,
            query="",
            offset="",
        ),
        InlineQueryHandler,
        "from_user",
        None,
        id="inline-query",
    ),
    pytest.param(
        raw.types.UpdateBotInlineSend(
            user_id=_EMPTY_ID,
            query="",
            id="result",
        ),
        ChosenInlineResultHandler,
        "from_user",
        None,
        id="chosen-inline-result",
    ),
    pytest.param(
        raw.types.UpdateBotPrecheckoutQuery(
            query_id=1,
            user_id=_EMPTY_ID,
            payload=b"payload",
            currency="XTR",
            total_amount=1,
        ),
        PreCheckoutQueryHandler,
        "from_user",
        None,
        id="pre-checkout-query",
    ),
    pytest.param(
        raw.types.UpdateBotShippingQuery(
            query_id=1,
            user_id=_EMPTY_ID,
            payload=b"payload",
            shipping_address=raw.types.PostAddress(
                street_line1="",
                street_line2="",
                city="",
                state="",
                country_iso2="",
                post_code="",
            ),
        ),
        ShippingQueryHandler,
        "from_user",
        None,
        id="shipping-query",
    ),
    pytest.param(
        raw.types.UpdateBotChatInviteRequester(
            peer=raw.types.PeerChat(chat_id=_GROUP_ID),
            date=1,
            user_id=_EMPTY_ID,
            about="",
            invite=raw.types.ChatInvitePublicJoinRequests(),
            qts=1,
        ),
        ChatJoinRequestHandler,
        "from_user",
        None,
        id="chat-join-request",
    ),
    pytest.param(
        raw.types.UpdateChatParticipant(
            chat_id=_GROUP_ID,
            date=1,
            actor_id=_EMPTY_ID,
            user_id=_SENDER_ID,
            qts=1,
        ),
        ChatMemberUpdatedHandler,
        "from_user",
        None,
        id="chat-member-actor",
    ),
    pytest.param(
        raw.types.UpdateChatParticipant(
            chat_id=_GROUP_ID,
            date=1,
            actor_id=_SENDER_ID,
            user_id=_SENDER_ID,
            new_participant=raw.types.ChatParticipant(
                user_id=_SENDER_ID,
                inviter_id=_EMPTY_ID,
                date=1,
            ),
            qts=1,
        ),
        ChatMemberUpdatedHandler,
        "new_chat_member.invited_by",
        None,
        id="chat-member-inviter",
    ),
    pytest.param(
        raw.types.UpdateChatParticipant(
            chat_id=_GROUP_ID,
            date=1,
            actor_id=_SENDER_ID,
            user_id=_SENDER_ID,
            invite=raw.types.ChatInviteExported(
                link="https://t.me/+link",
                admin_id=_EMPTY_ID,
                date=1,
            ),
            qts=1,
        ),
        ChatMemberUpdatedHandler,
        "invite_link.creator",
        None,
        id="chat-member-invite-link-creator",
    ),
    pytest.param(
        raw.types.UpdateBotMessageReaction(
            peer=raw.types.PeerUser(user_id=_EMPTY_ID),
            msg_id=1,
            date=1,
            actor=raw.types.PeerUser(user_id=_SENDER_ID),
            old_reactions=[],
            new_reactions=[],
            qts=1,
        ),
        MessageReactionHandler,
        "chat",
        None,
        id="reaction-chat",
    ),
    pytest.param(
        raw.types.UpdateBotMessageReaction(
            peer=raw.types.PeerChat(chat_id=_GROUP_ID),
            msg_id=1,
            date=1,
            actor=raw.types.PeerUser(user_id=_EMPTY_ID),
            old_reactions=[],
            new_reactions=[],
            qts=1,
        ),
        MessageReactionHandler,
        "user",
        None,
        id="reaction-actor",
    ),
    pytest.param(
        raw.types.UpdateBotMessageReactions(
            peer=raw.types.PeerUser(user_id=_EMPTY_ID),
            msg_id=1,
            date=1,
            reactions=[],
            qts=1,
        ),
        MessageReactionCountHandler,
        "chat",
        None,
        id="reaction-count-chat",
    ),
    pytest.param(
        raw.types.UpdateMessagePollVote(
            poll_id=1,
            peer=raw.types.PeerUser(user_id=_EMPTY_ID),
            options=[b"0"],
            positions=[],
            qts=1,
        ),
        PollHandler,
        "voter",
        None,
        id="poll-voter",
    ),
    pytest.param(
        _service_from(
            raw.types.MessageActionChatAddUser(users=[_EMPTY_ID]),
            sender_id=_SENDER_ID,
        ),
        MessageHandler,
        "new_chat_members",
        [None],
        id="new-chat-members-added",
    ),
    pytest.param(
        _service_from(
            raw.types.MessageActionChatJoinedByLink(inviter_id=_SENDER_ID),
            sender_id=_EMPTY_ID,
        ),
        MessageHandler,
        "new_chat_members",
        [None],
        id="new-chat-members-by-link",
    ),
    pytest.param(
        _service_from(raw.types.MessageActionChatJoinedByRequest(), sender_id=_EMPTY_ID),
        MessageHandler,
        "new_chat_members",
        [None],
        id="new-chat-members-by-request",
    ),
    pytest.param(
        _service_from(
            raw.types.MessageActionChatDeleteUser(user_id=_EMPTY_ID),
            sender_id=_SENDER_ID,
        ),
        MessageHandler,
        "left_chat_member",
        None,
        id="left-chat-member",
    ),
    pytest.param(
        _service_from(
            raw.types.MessageActionGameScore(
                game_id=1,
                score=1,
            ),
            sender_id=_EMPTY_ID,
        ),
        MessageHandler,
        "game_high_score.user",
        None,
        id="game-high-score",
    ),
    pytest.param(
        _service_from(
            raw.types.MessageActionInviteToGroupCall(
                call=raw.types.InputGroupCall(
                    id=1,
                    access_hash=1,
                ),
                users=[_EMPTY_ID],
            ),
            sender_id=_SENDER_ID,
        ),
        MessageHandler,
        "video_chat_members_invited.users",
        [None],
        id="video-chat-members-invited",
    ),
    pytest.param(
        raw.types.UpdateStory(
            peer=raw.types.PeerUser(user_id=_SENDER_ID),
            story=raw.types.StoryItem(
                id=1,
                date=1,
                expire_date=2,
                media=raw.types.MessageMediaEmpty(),
                fwd_from=raw.types.StoryFwdHeader(
                    from_peer=raw.types.PeerUser(user_id=_EMPTY_ID),
                    story_id=1,
                ),
                # What `StoryItem.read` gives for an absent flag, and what the parser iterates.
                media_areas=[],
            ),
        ),
        StoryHandler,
        "forward_from",
        None,
        id="story-forward-from",
    ),
    pytest.param(
        raw.types.UpdateDeleteEphemeralMessages(
            peer=raw.types.PeerUser(user_id=_EMPTY_ID),
            ids=[1],
        ),
        DeletedMessagesHandler,
        "0.chat",
        None,
        id="deleted-messages-chat",
    ),
    pytest.param(
        raw.types.UpdateDeleteEphemeralMessages(
            peer=raw.types.PeerChat(chat_id=_EMPTY_ID),
            ids=[1],
        ),
        DeletedMessagesHandler,
        "0.chat",
        None,
        id="deleted-messages-basic-group",
    ),
)


@pytest.mark.parametrize(
    ("update", "handler_type", "field", "expected"),
    _UPDATES_NAMING_AN_EMPTY_ENTITY,
)
async def test_an_update_naming_an_empty_entity_reaches_its_handler_without_it(
    client_with_storage: Client,
    update: raw.base.Update,
    handler_type: type[Handler[Any]],
    field: str,
    expected: list[None] | None,
) -> None:
    # The dispatcher drops `userEmpty` and `chatEmpty` from `users` and `chats`, and these
    #  parsers indexed them by id, so the update raised `KeyError` and no handler ran; on `main` the field was `None`.
    value = await _handled_field(
        client_with_storage,
        update=update,
        handler_type=handler_type,
        field=field,
        listed_user=raw.types.UserEmpty(id=_EMPTY_ID),
        listed_chat=raw.types.ChatEmpty(id=_EMPTY_ID),
    )

    assert value == expected


@pytest.mark.parametrize(
    ("update", "handler_type", "field", "expected"),
    _UPDATES_NAMING_AN_EMPTY_ENTITY,
)
async def test_an_update_naming_a_known_entity_reaches_its_handler_with_it(
    client_with_storage: Client,
    update: raw.base.Update,
    handler_type: type[Handler[Any]],
    field: str,
    expected: list[None] | None,
) -> None:
    # The same parsers now give `None` when the entity is missing, so the entity has to
    #  survive that check when the update lists it in full.
    value = await _handled_field(
        client_with_storage,
        update=update,
        handler_type=handler_type,
        field=field,
        listed_user=raw.types.User(
            id=_EMPTY_ID,
            first_name="Listed",
            access_hash=0,
        ),
        listed_chat=raw.types.Chat(
            id=_EMPTY_ID,
            title="Listed",
            photo=raw.types.ChatPhotoEmpty(),
            participants_count=2,
            date=1,
            version=1,
        ),
    )

    # A user id is positive and a basic group id is its negative, so both read as `_EMPTY_ID`.
    ids = [abs(item.id) for item in value] if isinstance(value, list) else abs(value.id)
    assert ids == ([_EMPTY_ID] if isinstance(expected, list) else _EMPTY_ID)


async def _handled_field(
    client: Client,
    *,
    update: raw.base.Update,
    handler_type: type[Handler[Any]],
    field: str,
    listed_user: raw.base.User,
    listed_chat: raw.base.Chat,
) -> Any:
    """The field of what the handler got for an update listing these entities at `_EMPTY_ID`."""
    received: list[Any] = []

    async def record(client: Client, parsed: Any, /) -> None:
        received.append(parsed)

    client.add_handler(handler_type(record))

    await client.dispatcher.start()
    await client.handle_updates(
        raw.types.Updates(
            updates=[update],
            users=[
                listed_user,
                raw.types.User(
                    id=_SENDER_ID,
                    first_name="Sender",
                    access_hash=0,
                ),
            ],
            chats=[_GROUP, listed_chat],
            date=1,
            seq=1,
        ),
    )
    await client.dispatcher.stop()

    [parsed] = received
    value: Any = parsed
    for name in field.split("."):
        value = value[int(name)] if name.isdigit() else getattr(value, name)

    return value


@pytest.fixture
def frequent_thread_switches() -> Iterator[None]:
    """Switch threads inside the copy-and-rebind rather than around it.

    The default interval is 5ms, which is far longer than a registration takes, so two
    threads interleave inside one only by luck.
    """
    previous = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)

    try:
        yield

    finally:
        sys.setswitchinterval(previous)


@pytest.mark.usefixtures("frequent_thread_switches")
def test_handlers_registered_from_two_threads_at_once_all_survive(client: Client) -> None:
    def register() -> None:
        for _ in range(_HANDLERS_PER_THREAD):
            client.add_handler(MessageHandler(greet))

    threads = [threading.Thread(target=register) for _ in range(_REGISTERING_THREADS)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    registered = sum(len(handlers) for handlers in client.dispatcher.groups.values())

    assert registered == _HANDLERS_PER_THREAD * _REGISTERING_THREADS
