"""Keep every public rich node represented in both output formats."""

import warnings
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from pyrogram import types
from pyrogram.parser.rich_message import UnsupportedRichContentWarning
from pyrogram.types.messages_and_media import rich_block, rich_text


PARAGRAPH = types.RichBlockParagraph(text="content")
CAPTION = types.RichBlockCaption(text="caption", credit="author")
BUTTON = types.RichMessageButton(text="button", url="https://example.com")
MEDIA = SimpleNamespace(file_id="file-id")

BLOCKS = [
    PARAGRAPH,
    types.RichBlockSectionHeading(text="heading", size=1),
    types.RichBlockPreformatted(text="code", language="python"),
    types.RichBlockFooter(text="footer"),
    types.RichBlockDivider(),
    types.RichBlockMathematicalExpression(expression="x+y"),
    types.RichBlockAnchor(name="anchor"),
    types.RichBlockList(items=[types.RichBlockListItem(label="•", blocks=[PARAGRAPH])]),
    types.RichBlockBlockQuotation(blocks=[PARAGRAPH], credit="author"),
    types.RichBlockExpandableBlockQuotation(text="quote", credit="author"),
    types.RichBlockPullQuotation(text="quote", credit="author"),
    types.RichBlockCollage(blocks=[types.RichBlockPhoto(photo=MEDIA)], caption=CAPTION),
    types.RichBlockSlideshow(blocks=[types.RichBlockPhoto(photo=MEDIA)], caption=CAPTION),
    types.RichBlockTable(
        cells=[[types.RichBlockTableCell(text="cell")]],
        caption=CAPTION,
        is_bordered=True,
        is_striped=True,
        is_compact=True,
    ),
    types.RichBlockDetails(summary="summary", blocks=[PARAGRAPH], is_open=True),
    types.RichBlockMap(
        location=types.Location(latitude=1, longitude=2),
        zoom=3,
        width=100,
        height=100,
        caption=CAPTION,
    ),
    types.RichBlockButtons(buttons=[BUTTON], align="center"),
    types.RichBlockAnimation(animation=MEDIA, has_spoiler=True, caption=CAPTION),
    types.RichBlockAudio(audio=MEDIA, caption=CAPTION),
    types.RichBlockDocument(document=MEDIA, caption=CAPTION),
    types.RichBlockPhoto(photo=MEDIA, has_spoiler=True, caption=CAPTION),
    types.RichBlockVideo(video=MEDIA, has_spoiler=True, caption=CAPTION),
    types.RichBlockVoiceNote(voice_note=MEDIA, caption=CAPTION),
    types.RichBlockThinking(text="thinking"),
]

TEXTS = [
    types.RichTextBold(text="bold"),
    types.RichTextItalic(text="italic"),
    types.RichTextUnderline(text="underline"),
    types.RichTextStrikethrough(text="strikethrough"),
    types.RichTextSpoiler(text="spoiler"),
    types.RichTextDateTime(
        text="date", date=datetime(2026, 1, 1, tzinfo=timezone.utc), date_time_format="r"
    ),
    types.RichTextTextMention(text="mention", user=types.User(id=42)),
    types.RichTextSubscript(text="subscript"),
    types.RichTextSuperscript(text="superscript"),
    types.RichTextMarked(text="marked"),
    types.RichTextCode(text="code"),
    types.RichTextCustomEmoji(custom_emoji_id="123", alternative_text="🙂"),
    types.RichTextMathematicalExpression(expression="x+y"),
    types.RichTextUrl(text="url", url="https://example.com"),
    types.RichTextEmailAddress(text="email", email_address="a@example.com"),
    types.RichTextPhoneNumber(text="phone", phone_number="+123"),
    types.RichTextBankCardNumber(text="card", bank_card_number="1234"),
    types.RichTextMention(text="@name", username="name"),
    types.RichTextHashtag(text="#tag", hashtag="tag"),
    types.RichTextCashtag(text="$USD", cashtag="USD"),
    types.RichTextBotCommand(text="/start", bot_command="start"),
    types.RichTextButton(button=BUTTON),
    types.RichTextAnchor(text="anchor", name="a"),
    types.RichTextAnchorLink(text="anchor link", anchor_name="a"),
    types.RichTextReference(text="reference", name="r"),
    types.RichTextReferenceLink(text="reference link", reference_name="r"),
]


def test_every_public_node_has_a_rendering_case():
    block_classes = {
        value
        for value in vars(rich_block).values()
        if isinstance(value, type) and issubclass(value, types.RichBlock)
    }
    nested_blocks = {types.RichBlockCaption, types.RichBlockTableCell, types.RichBlockListItem}

    assert block_classes - nested_blocks - {types.RichBlock, types.RichBlockUnsupported} == {
        type(node) for node in BLOCKS
    }

    text_classes = {
        value
        for value in vars(rich_text).values()
        if isinstance(value, type) and issubclass(value, types.RichText)
    }

    assert text_classes - {types.RichText, types.RichTextUnsupported} == {
        type(node) for node in TEXTS
    }


@pytest.mark.parametrize("format", ["html", "markdown"])
@pytest.mark.parametrize("block", BLOCKS, ids=lambda node: type(node).__name__)
def test_every_block_renders_without_unsupported_warnings(block, format):
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnsupportedRichContentWarning)
        assert getattr(types.RichMessage(blocks=[block]), format)


@pytest.mark.parametrize("format", ["html", "markdown"])
@pytest.mark.parametrize("text", TEXTS, ids=lambda node: type(node).__name__)
def test_every_text_renders_without_unsupported_warnings(text, format):
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnsupportedRichContentWarning)
        assert getattr(types.RichMessage(blocks=[types.RichBlockParagraph(text=text)]), format)
