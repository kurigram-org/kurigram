"""Exercise server constructors, not just manually constructed public buttons."""

import asyncio
import re
import warnings
from pathlib import Path

import pytest

from pyrogram import raw, types
from pyrogram.parser.rich_message import UnsupportedRichContentWarning


INCOMING = [
    (
        raw.types.InlineButtonTypeUrl(url="https://example.com"),
        'type="url" url="https://example.com"',
    ),
    (
        raw.types.InlineButtonTypeUrlAuth(
            url="https://example.com", button_id=42, fwd_text="Forward"
        ),
        'type="login_url" url="https://example.com" forward-text="Forward"',
    ),
    (
        raw.types.InlineButtonTypeWebView(url="https://example.com"),
        'type="web_app" url="https://example.com"',
    ),
    (raw.types.InlineButtonTypeCallback(data=b"callback"), 'type="callback_data" data="callback"'),
    (raw.types.InlineButtonTypeSwitchInline(query=""), 'type="switch_inline_query" query=""'),
    (
        raw.types.InlineButtonTypeSwitchInline(query="q", same_peer=True),
        'type="switch_inline_query_current_chat" query="q"',
    ),
    (
        raw.types.InlineButtonTypeSwitchInline(
            query="q",
            peer_types=[
                raw.types.InlineQueryPeerTypePM(),
                raw.types.InlineQueryPeerTypeBotPM(),
                raw.types.InlineQueryPeerTypeChat(),
                raw.types.InlineQueryPeerTypeBroadcast(),
            ],
        ),
        'type="switch_inline_query_chosen_chat" query="q" allow-user-chats allow-bot-chats allow-group-chats allow-channel-chats',
    ),
    (
        raw.types.InlineButtonTypeUserProfile(user_id=799280805),
        'type="url" url="tg://user?id=799280805"',
    ),
    (raw.types.InlineButtonTypeCopy(copy_text="copy"), 'type="copy_text" text="copy"'),
    (raw.types.InlineButtonTypeDisabled(), 'type="disabled"'),
]

# These actions belong to ordinary inline keyboards; rich HTML has no equivalent.
UNSUPPORTED = [raw.types.InlineButtonTypeGame, raw.types.InlineButtonTypeBuy]
# Input-only variants are written by clients, not returned in received messages.
INPUT_ONLY = {"inputInlineButtonTypeUrlAuth", "inputInlineButtonTypeUserProfile"}


def test_all_schema_button_constructors_are_accounted_for():
    schema = Path(__file__).resolve().parents[3] / "compiler/api/source/main_api.tl"
    names = set(re.findall(r"^(\w+)#[^\n]* = InlineButtonType;", schema.read_text(), re.M))
    incoming = {
        type(action).__name__[0].lower() + type(action).__name__[1:] for action, _ in INCOMING
    }
    unsupported = {cls.__name__[0].lower() + cls.__name__[1:] for cls in UNSUPPORTED}

    assert names == incoming | unsupported | INPUT_ONLY


@pytest.mark.parametrize("format", ["html", "markdown"])
@pytest.mark.parametrize("inline", [True, False])
@pytest.mark.parametrize(
    "action,expected",
    INCOMING,
    ids=lambda value: type(value).__name__ if not isinstance(value, str) else value,
)
def test_received_buttons_parse_and_render(action, expected, inline, format):
    label = raw.types.TextPlain(text="@userrr")
    if inline:
        incoming = raw.types.PageBlockParagraph(text=raw.types.TextButton(text=label, type=action))
    else:
        incoming = raw.types.PageBlockButtonRow(
            buttons=[raw.types.PageButton(text=label, type=action)], align_center=True
        )

    block = asyncio.run(types.RichBlock._parse(None, incoming))

    with warnings.catch_warnings():
        warnings.simplefilter("error", UnsupportedRichContentWarning)
        rendered = getattr(types.RichMessage(blocks=[block]), format)

    assert f"<tg-button {expected}>@userrr</tg-button>" in rendered
    if not inline:
        assert '<tg-button-row align="center">' in rendered


@pytest.mark.parametrize("action", UNSUPPORTED)
def test_actions_without_rich_equivalent_warn_with_original_payload(action):
    incoming = raw.types.TextButton(text=raw.types.TextPlain(text="Label"), type=action())
    text = asyncio.run(types.RichText._parse(None, incoming))

    with pytest.warns(UnsupportedRichContentWarning) as caught:
        rendered = types.RichMessage(blocks=[types.RichBlockParagraph(text=text)]).html

    assert rendered == "<p>Label</p>"
    assert repr(incoming) in str(caught[0].message)


def test_received_profile_button_keeps_style_and_writes_a_profile_link():
    incoming = raw.types.TextButton(
        text=raw.types.TextPlain(text='Dev ("\u2067;("'),
        type=raw.types.InlineButtonTypeUserProfile(user_id=799280805),
        style=raw.types.RichButtonStyle(bg_success=True),
    )

    async def parse_and_write():
        button = await types.RichMessageButton._parse(None, incoming)
        return button, await button.write(None)

    button, written = asyncio.run(parse_and_write())

    assert button.url == "tg://user?id=799280805"
    assert button.text == incoming.text.text
    assert written.type.url == button.url
    assert written.style.bg_success is True
