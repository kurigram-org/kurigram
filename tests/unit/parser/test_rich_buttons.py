import asyncio
import inspect
import warnings
from datetime import datetime, timezone
from html.parser import HTMLParser

import pytest

from pyrogram import enums, raw, types
from pyrogram.parser.rich_message import UnsupportedRichContentWarning


class Tags(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.tags = []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


BUTTONS = [
    (
        {"url": 'https://example.com/?a=1&b="2"'},
        {"type": "url", "url": 'https://example.com/?a=1&b="2"'},
    ),
    ({"url": "tg://user?id=42"}, {"type": "url", "url": "tg://user?id=42"}),
    ({"callback_data": "שלום<&"}, {"type": "callback_data", "data": "שלום<&"}),
    ({"callback_data": b"data"}, {"type": "callback_data", "data": "data"}),
    (
        {"web_app": types.WebAppInfo(url="https://example.com")},
        {"type": "web_app", "url": "https://example.com"},
    ),
    (
        {
            "login_url": types.LoginUrl(
                url="https://example.com", forward_text="forward", request_write_access=True
            )
        },
        {
            "type": "login_url",
            "url": "https://example.com",
            "forward-text": "forward",
            "request-write-access": None,
        },
    ),
    ({"switch_inline_query": ""}, {"type": "switch_inline_query", "query": ""}),
    (
        {"switch_inline_query_current_chat": ""},
        {"type": "switch_inline_query_current_chat", "query": ""},
    ),
    (
        {
            "switch_inline_query_chosen_chat": types.SwitchInlineQueryChosenChat(
                query="q",
                allow_user_chats=True,
                allow_bot_chats=True,
                allow_group_chats=True,
                allow_channel_chats=True,
            )
        },
        {
            "type": "switch_inline_query_chosen_chat",
            "query": "q",
            "allow-user-chats": None,
            "allow-bot-chats": None,
            "allow-group-chats": None,
            "allow-channel-chats": None,
        },
    ),
    ({"copy_text": "copy<&"}, {"type": "copy_text", "text": "copy<&"}),
    ({"disabled": types.DisabledButton()}, {"type": "disabled"}),
]


@pytest.mark.parametrize("format", ["html", "markdown"])
@pytest.mark.parametrize("inline", [False, True])
@pytest.mark.parametrize("kwargs,expected", BUTTONS)
def test_button_actions(format, inline, kwargs, expected):
    button = types.RichMessageButton(text="Button", **kwargs)
    block = (
        types.RichBlockParagraph(text=types.RichTextButton(button=button))
        if inline
        else types.RichBlockButtons(buttons=[button])
    )

    with warnings.catch_warnings():
        warnings.simplefilter("error", UnsupportedRichContentWarning)
        result = getattr(types.RichMessage(blocks=[block]), format)

    assert ("tg-button", expected) in Tags(result).tags
    assert ">Button</tg-button>" in result


@pytest.mark.parametrize("style", list(enums.ButtonStyle))
@pytest.mark.parametrize("align", [None, "left", "center", "right"])
def test_button_style_alignment_and_formatted_label(style, align):
    button = types.RichMessageButton(
        text=[
            "Go ",
            types.RichTextCustomEmoji(custom_emoji_id="123", alternative_text="🙂"),
            types.RichTextDateTime(
                text="today", date=datetime(2026, 1, 1, tzinfo=timezone.utc), date_time_format="D"
            ),
        ],
        callback_data="payload",
        style=style,
    )
    message = types.RichMessage(blocks=[types.RichBlockButtons(buttons=[button], align=align)])
    parsed = Tags(message.html).tags

    assert ("tg-button-row", {} if align is None else {"align": align}) in parsed
    attributes = next(attrs for tag, attrs in parsed if tag == "tg-button")
    assert attributes.get("style") == (None if style == enums.ButtonStyle.DEFAULT else style.value)
    assert '<tg-emoji emoji-id="123">🙂</tg-emoji>' in message.html
    assert '<tg-time unix="1767225600" format="D">today</tg-time>' in message.html
    assert message.markdown == message.html


def test_expandable_quote_with_credit():
    message = types.RichMessage(
        blocks=[
            types.RichBlockExpandableBlockQuotation(
                text=types.RichTextBold(text="quote"), credit="author"
            )
        ]
    )

    assert message.html == "<blockquote expandable><b>quote</b><cite>author</cite></blockquote>"
    assert message.markdown == message.html


def test_button_text_is_preserved_in_plain_text_contexts():
    button = types.RichTextButton(
        button=types.RichMessageButton(text="button label", disabled=types.DisabledButton())
    )
    message = types.RichMessage(blocks=[types.RichBlockPreformatted(text=button)])

    assert message.html == "<pre>button label</pre>"
    assert types.RichText._to_plain_text(button) == "button label"


def test_unknown_raw_block_warning_contains_original_payload():
    incoming = raw.types.PageBlockEmbed(
        url="https://example.com/unsupported",
        html="original content",
        caption=raw.types.PageCaption(text=raw.types.TextEmpty(), credit=raw.types.TextEmpty()),
    )
    block = asyncio.run(types.RichBlock._parse(None, incoming))

    with pytest.warns(UnsupportedRichContentWarning) as caught:
        assert types.RichMessage(blocks=[block]).html == ""

    warning = str(caught[0].message)
    assert "blocks[0]" in warning
    assert repr(incoming) in warning
    assert "original content" in warning


def test_unknown_raw_text_warning_contains_original_payload():
    incoming = raw.types.TextImage(document_id=12345, w=32, h=16)
    text = asyncio.run(types.RichText._parse(None, incoming))

    with pytest.warns(UnsupportedRichContentWarning) as caught:
        assert types.RichMessage(blocks=[types.RichBlockParagraph(text=text)]).html == "<p></p>"

    assert repr(incoming) in str(caught[0].message)


def test_binary_callback_warns_with_data_and_preserves_label():
    button = types.RichMessageButton(text="Readable", callback_data=b"\xff")
    message = types.RichMessage(
        blocks=[types.RichBlockParagraph(text=types.RichTextButton(button=button))]
    )

    with pytest.warns(UnsupportedRichContentWarning, match="UTF-8") as caught:
        assert message.html == "<p>Readable</p>"

    assert repr(b"\xff") in str(caught[0].message)


def test_button_inline_markdown_punctuation_is_literal():
    message = types.RichMessage(
        blocks=[
            types.RichBlockParagraph(
                text=types.RichTextButton(
                    button=types.RichMessageButton(text="*literal*", url="https://example.com")
                )
            )
        ]
    )

    assert ">*literal*</tg-button>" in message.html
    assert ">&#42;literal&#42;</tg-button>" in message.markdown


def test_unknown_button_action_warning_retains_raw_action():
    incoming = raw.types.PageButton(
        text=raw.types.TextPlain(text="Play"), type=raw.types.InlineButtonTypeGame()
    )
    button = asyncio.run(types.RichMessageButton._parse(None, incoming))

    with pytest.warns(UnsupportedRichContentWarning) as caught:
        assert (
            types.RichMessage(blocks=[types.RichBlockButtons(buttons=[button])]).html
            == "<tg-button-row>Play</tg-button-row>"
        )

    assert repr(incoming) in str(caught[0].message)


def test_every_button_action_has_a_rendering_case():
    actions = set(inspect.signature(types.RichMessageButton).parameters) - {"text", "style"}

    assert actions == {field for kwargs, _ in BUTTONS for field in kwargs}


def test_login_for_another_bot_warns_without_changing_authorization_target():
    button = types.RichMessageButton(
        text="Login", login_url=types.LoginUrl(url="https://example.com", bot_username="otherbot")
    )
    message = types.RichMessage(
        blocks=[types.RichBlockParagraph(text=types.RichTextButton(button=button))]
    )

    with pytest.warns(UnsupportedRichContentWarning, match="bot_username") as caught:
        assert message.html == "<p>Login</p>"

    assert "otherbot" in str(caught[0].message)
