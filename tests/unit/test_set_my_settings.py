from pyrogram import Client


class FakeClient:
    set_my_settings = Client.set_my_settings

    async def invoke(self, query):
        self.query = query


async def test_unspecified_settings_are_left_alone():
    client = FakeClient()

    assert await client.set_my_settings() is True
    assert all(getattr(client.query, name) is None for name in client.query.__slots__)


async def test_join_groups_and_default_callback_mode_are_translated():
    client = FakeClient()
    await client.set_my_settings(can_join_groups=False, callback_query_mode="default")

    assert client.query.nochats is True
    assert client.query.callback_mode == ""

    await client.set_my_settings(can_join_groups=True, callback_query_mode="inline")

    assert client.query.nochats is False
    assert client.query.callback_mode == "inline"
