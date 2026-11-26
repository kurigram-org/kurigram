from io import BytesIO

import pytest

from pyrogram import Client, raw, types
from pyrogram.raw.core import TLObject


@pytest.mark.parametrize(
    "obj, field, element_type",
    [
        (
            raw.types.InputPrivacyValueAllowUsers(users=[raw.types.InputUserSelf()]),
            "users",
            raw.types.InputUserSelf,
        ),
        (
            raw.functions.messages.SendReaction(
                peer=raw.types.InputPeerSelf(), msg_id=1, reaction=[raw.types.ReactionPaid()]
            ),
            "reaction",
            raw.types.ReactionPaid,
        ),
    ],
)
def test_vector_of_fieldless_objects(obj, field, element_type):
    data = obj.write()
    restored = TLObject.read(BytesIO(data))
    assert isinstance(getattr(restored, field)[0], element_type)
    assert restored.write() == data


@pytest.mark.parametrize("slots", [None, [], [1, 2]])
def test_boost_status_optional_slots(slots):
    status = raw.types.premium.BoostsStatus(
        level=1,
        current_level_boosts=1,
        boosts=1,
        boost_url="url",
        my_boost=slots is not None,
        my_boost_slots=slots,
    )
    decoded = TLObject.read(BytesIO(status.write()))
    assert decoded.my_boost_slots == slots
    assert types.BoostsStatus._parse(decoded).my_boost_slots == (slots or None)


@pytest.mark.parametrize("solution, entities", [(None, None), ("answer", [])])
def test_poll_solution_round_trip(solution, entities):
    poll = raw.types.Poll(
        id=1, question=raw.types.TextWithEntities(text="?", entities=[]), answers=[], hash=0
    )
    media = raw.types.InputMediaPoll(poll=poll, solution=solution, solution_entities=entities)
    wire = media.write()
    assert bool(wire[4] & 2) == (solution is not None)
    restored = TLObject.read(BytesIO(wire))
    assert restored.solution_entities == entities
    assert restored.write() == wire


def test_replacing_an_absent_vector():
    request = raw.functions.auth.InitFirebasePnvLogin(api_id=1, api_hash="hash")
    restored = TLObject.read(BytesIO(request.write()))
    assert restored.except_ids is None
    restored.except_ids = [42]
    assert TLObject.read(BytesIO(restored.write())).except_ids == [42]
    restored.except_ids = []
    assert restored.write()[4] & 1


@pytest.mark.asyncio
async def test_poll_update_without_results():
    update = raw.types.UpdateMessagePoll(poll_id=1, results=raw.types.PollResults())
    parsed = await types.Poll._parse_update(None, TLObject.read(BytesIO(update.write())))
    assert parsed.options == []


@pytest.mark.asyncio
@pytest.mark.parametrize("ephemeral", [False, True])
async def test_plain_poll_description_without_entities(ephemeral):
    client = Client("test", api_id=1, api_hash="0" * 32, in_memory=True)
    peer = raw.types.PeerUser(user_id=1)
    media = raw.types.MessageMediaPoll(
        poll=raw.types.Poll(
            id=1, question=raw.types.TextWithEntities(text="?", entities=[]), answers=[], hash=0
        ),
        results=raw.types.PollResults(),
    )
    fields = {"id": 1, "peer_id": peer, "date": 1, "message": "Plain description", "media": media}
    if ephemeral:
        message = raw.types.EphemeralMessage(from_id=peer, receiver_id=1, **fields)
    else:
        message = raw.types.Message(**fields)
    parsed = await types.Message._parse(
        client, TLObject.read(BytesIO(message.write())), {1: raw.types.User(id=1)}, {}, replies=0
    )
    assert parsed.poll.description.text == "Plain description"
