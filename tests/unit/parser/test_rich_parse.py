import asyncio

import pytest

from pyrogram import raw, types


def parse_text(text, **kwargs):
    return asyncio.run(types.RichText._parse(None, text, **kwargs))


def parse_block(block, **kwargs):
    return asyncio.run(types.RichBlock._parse(None, block, **kwargs))


def mention():
    return raw.types.TextMentionName(text=raw.types.TextPlain(text="Ada"), user_id=42)


def users():
    return {42: raw.types.User(id=42, first_name="Ada", usernames=[], restriction_reason=[])}


def caption(text=None):
    return raw.types.PageCaption(text=text or raw.types.TextEmpty(), credit=raw.types.TextEmpty())


def test_empty_text_is_readable_empty_string():
    assert parse_text(raw.types.TextEmpty()) == ""
    assert parse_text(None) is None


def test_unknown_text_preserves_type_and_readable_nested_content():
    class FutureText:
        text = raw.types.TextBold(text=mention())

    parsed = parse_text(FutureText(), users=users())

    assert parsed.original_type == "FutureText"
    assert parsed.text.text.user.id == 42
    assert types.RichText._to_plain_text(parsed) == "Ada"
    assert isinstance(parsed, types.RichTextUnsupported)


def test_unknown_text_and_block_keep_raw_payload():
    class FutureBlock:
        content = "unsupported payload"

    text = parse_text(FutureBlock())
    block = parse_block(FutureBlock())

    assert text.original_type == block.original_type == "FutureBlock"
    assert text.text is None
    assert block.raw.content == text.raw.content == "unsupported payload"
    assert types.RichBlockUnsupported().original_type is None


def test_nested_mentions_preserve_users():
    parsed = parse_block(
        raw.types.PageBlockParagraph(
            text=raw.types.TextConcat(
                texts=[raw.types.TextBold(text=raw.types.TextItalic(text=mention()))]
            )
        ),
        users=users(),
    )

    assert parsed.text[0].text.text.user.id == 42


def test_table_caption_and_cells_preserve_mentions():
    parsed = parse_block(
        raw.types.PageBlockTable(
            title=mention(),
            rows=[raw.types.PageTableRow(cells=[raw.types.PageTableCell(text=mention())])],
        ),
        users=users(),
    )

    assert isinstance(parsed.caption, types.RichBlockCaption)
    assert parsed.caption.text.user.id == 42
    assert parsed.cells[0][0].text.user.id == 42


@pytest.mark.parametrize("ordered", [False, True])
def test_nested_list_keeps_media_and_caption_context(ordered):
    document = raw.types.Document(
        id=8,
        access_hash=9,
        file_reference=b"ref",
        date=1,
        mime_type="application/pdf",
        size=12,
        dc_id=2,
        thumbs=[],
        attributes=[raw.types.DocumentAttributeFilename(file_name="sample.pdf")],
    )
    photo = raw.types.Photo(
        id=3,
        access_hash=4,
        file_reference=b"ref",
        date=1,
        dc_id=2,
        sizes=[raw.types.PhotoSize(type="x", w=10, h=20, size=12)],
    )
    blocks = [
        raw.types.PageBlockDocument(document_id=8, caption=caption(mention())),
        raw.types.PageBlockPhoto(photo_id=3, caption=caption(mention())),
    ]
    nested = raw.types.PageBlockList(items=[raw.types.PageListItemBlocks(blocks=blocks)])

    if ordered:
        source = raw.types.PageBlockOrderedList(
            items=[raw.types.PageListOrderedItemBlocks(num="1", blocks=[nested])]
        )
    else:
        source = raw.types.PageBlockList(items=[raw.types.PageListItemBlocks(blocks=[nested])])

    parsed = parse_block(source, documents={8: document}, photos={3: photo}, users=users())
    doc_block, photo_block = parsed.items[0].blocks[0].items[0].blocks

    assert isinstance(doc_block, types.RichBlockDocument)
    assert doc_block.document.file_name == "sample.pdf"
    assert doc_block.document.mime_type == "application/pdf"
    assert doc_block.caption.text.user.id == 42
    assert photo_block.photo.width == 10
    assert photo_block.caption.text.user.id == 42


@pytest.mark.parametrize(
    "raw_type,field,value",
    [
        (raw.types.TextAutoUrl, "url", "https://example.com"),
        (raw.types.TextAutoEmail, "email_address", "ada@example.com"),
        (raw.types.TextAutoPhone, "phone_number", "+123456789"),
        (raw.types.TextBankCard, "bank_card_number", "1234 5678"),
    ],
)
def test_automatic_targets_are_plain_strings_with_formatted_display(raw_type, field, value):
    content = raw.types.TextConcat(
        texts=[
            raw.types.TextBold(text=raw.types.TextPlain(text=value[:4])),
            raw.types.TextPlain(text=value[4:]),
        ]
    )
    parsed = parse_text(raw_type(text=content))

    assert getattr(parsed, field) == value
    assert isinstance(parsed.text[0], types.RichTextBold)
    assert types.RichText._to_plain_text(parsed.text) == value


def test_audio_block_preserves_voice_note_type_and_caption():
    document = raw.types.Document(
        id=8,
        access_hash=9,
        file_reference=b"ref",
        date=1,
        mime_type="audio/ogg",
        size=12,
        dc_id=2,
        thumbs=[],
        attributes=[raw.types.DocumentAttributeAudio(duration=3, voice=True, waveform=b"wave")],
    )
    parsed = parse_block(
        raw.types.PageBlockAudio(audio_id=8, caption=caption(raw.types.TextPlain(text="Voice"))),
        documents={8: document},
    )

    assert isinstance(parsed, types.RichBlockVoiceNote)
    assert parsed.voice_note.duration == 3
    assert parsed.caption.text == "Voice"
