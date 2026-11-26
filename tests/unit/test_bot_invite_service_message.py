from pyrogram import Client, enums, raw, types


async def test_bot_invite_is_write_access_allowed_with_inviter():
    client = Client("test", in_memory=True)
    message = raw.types.MessageService(
        id=1,
        peer_id=raw.types.PeerUser(user_id=42),
        date=0,
        action=raw.types.MessageActionBotInvite(inviter_id=42),
    )
    users = {42: raw.types.User(id=42, first_name="Owner")}

    parsed = await types.Message._parse(client, message, users, {}, replies=0)

    assert parsed.service == enums.MessageServiceType.WRITE_ACCESS_ALLOWED
    assert parsed.write_access_allowed.inviter.id == 42
