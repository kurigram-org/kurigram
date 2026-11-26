import pytest

from pyrogram import Client, raw, types


@pytest.mark.parametrize(
    ("bot", "nochats", "expected"),
    [(True, False, True), (True, True, False), (False, False, None)],
)
async def test_can_join_groups_is_the_inverse_of_bot_nochats(bot, nochats, expected):
    user = raw.types.User(id=1, first_name="x", bot=bot, bot_nochats=nochats)

    parsed = await types.User._parse(Client("test", in_memory=True), user)

    assert parsed.can_join_groups is expected
