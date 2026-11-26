from pyrogram import raw, types, utils


class FakeClient:
    async def resolve_peer(self, peer_id):
        if peer_id is None:
            return None

        return raw.types.InputPeerUser(user_id=peer_id, access_hash=0)


async def test_omitted_receiver_is_sent_empty():
    parameters = types.EphemeralMessageParameters(callback_query_id="1")
    receiver = await utils.get_ephemeral_receiver(FakeClient(), parameters.receiver_user_id)

    assert isinstance(receiver, raw.types.InputUserEmpty)


async def test_given_receiver_is_resolved():
    receiver = await utils.get_ephemeral_receiver(FakeClient(), 42)

    assert receiver.user_id == 42
