import asyncio
import warnings
from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace

import pytest

from pyrogram import raw, types
from pyrogram.parser.rich_message import UnsupportedRichContentWarning

DOCUMENT_ID = "BQACAgIAAx0CAAGgr9AAAgmPX7b4UxbjNoFEO_L0I4s6wrXNJA8AAgQAA4GkuUm9FFvIaOhXWR4E"


def message(*blocks):
    return types.RichMessage(blocks=list(blocks))


def test_nested_inline_and_escaping():
    rich = message(
        types.RichBlockParagraph(
            text=[
                types.RichTextBold(text=["bold ", types.RichTextItalic(text="italic")]),
                " <&> *literal*",
            ]
        )
    )

    assert rich.html == "<p><b>bold <i>italic</i></b> &lt;&amp;&gt; *literal*</p>"
    assert rich.markdown == "**bold *italic*** &lt;&amp;&gt; \\*literal\\*"


def test_blocks_and_complex_table():
    rich = message(
        types.RichBlockSectionHeading(text="Title", size=2),
        types.RichBlockTable(
            cells=[
                [types.RichBlockTableCell(text="A", is_header=True, colspan=2)],
                [
                    types.RichBlockTableCell(text="B"),
                    types.RichBlockTableCell(text="C"),
                ],
            ],
            is_bordered=True,
        ),
    )

    assert rich.markdown.startswith("## Title\n\n<table bordered>")
    assert '<th colspan="2">A</th>' in rich.html


def test_simple_table():
    rich = message(
        types.RichBlockTable(
            cells=[
                [types.RichBlockTableCell(text="A", is_header=True)],
                [types.RichBlockTableCell(text="a|b")],
            ]
        )
    )

    assert rich.markdown == "| A |\n| :--- |\n| a\\|b |"


def test_unknown_block_warns_with_contents_and_skips():
    class FutureBlock(types.RichBlock):
        def __init__(self):
            super().__init__()

            self.content = "unsupported content"

    rich = message(FutureBlock(), types.RichBlockParagraph(text="kept"))

    with pytest.warns(UserWarning, match=r"FutureBlock.*blocks\[0\]") as caught:
        assert rich.html == "<p>kept</p>"

    assert "unsupported content" in str(caught[0].message)

    with pytest.warns(UserWarning):
        assert message(FutureBlock()).markdown == ""


def test_unknown_inline_preserves_text_and_known_errors_propagate():
    class FutureText(types.RichText):
        text = "kept <text>"

    with pytest.warns(UserWarning, match="FutureText"):
        assert (
            message(types.RichBlockParagraph(text=FutureText())).html == "<p>kept &lt;text&gt;</p>"
        )

    with pytest.raises(AttributeError):
        _ = message(types.RichBlockPhoto(photo=None)).html


def test_embedded_media_and_to_input():
    rich = types.RichMessage(
        blocks=[types.RichBlockPhoto(photo=SimpleNamespace(file_id="photo-id"))],
        is_rtl=True,
    )

    assert rich.markdown == "![](tg://photo?id=photo-id)"
    assert rich.html == '<img src="tg://photo?id=photo-id"/>'
    outgoing = rich.to_input(format="markdown")

    assert outgoing.markdown == rich.markdown
    assert outgoing.media is None
    assert outgoing.is_rtl is True

    with pytest.raises(ValueError):
        rich.to_input(format="invalid")


def test_input_document_file_mapping():
    outgoing = types.InputRichMessage(markdown=f"![](tg://document?id={DOCUMENT_ID})")
    result = write(outgoing)

    assert isinstance(result, raw.types.InputRichMessageMarkdown)
    assert isinstance(result.files[0], raw.types.InputRichFileDocument)
    assert result.files[0].id == "media_1"
    assert result.files[0].document.id == 5312458109417947140
    assert write(result)


@pytest.mark.parametrize("kwargs", [{}, {"html": "a", "markdown": "b"}, {"html": ""}])
def test_input_rejects_ambiguous_or_empty_format(kwargs):
    with pytest.raises(ValueError):
        write(types.InputRichMessage(**kwargs))


def test_html_fallback_uses_html_children():
    rich = message(
        types.RichBlockDetails(
            summary="Title",
            blocks=[types.RichBlockParagraph(text=types.RichTextBold(text="B"))],
            is_open=True,
        )
    )

    assert rich.markdown == "<details open><summary>Title</summary><p><b>B</b></p></details>"


def test_code_fences_and_inline_backticks():
    rich = message(types.RichBlockPreformatted(text="```\nhello", language="python"))

    assert rich.markdown == "````python\n```\nhello\n````"
    assert (
        message(types.RichBlockParagraph(text=types.RichTextCode(text="`a`"))).markdown
        == "`` `a` ``"
    )


@pytest.mark.parametrize(
    "cls,tag",
    [
        (types.RichTextUnderline, "u"),
        (types.RichTextStrikethrough, "s"),
        (types.RichTextSpoiler, "tg-spoiler"),
        (types.RichTextMarked, "mark"),
        (types.RichTextSubscript, "sub"),
        (types.RichTextSuperscript, "sup"),
    ],
)
def test_inline_styles(cls, tag):
    rich = message(types.RichBlockParagraph(text=cls(text="a&b")))

    assert rich.html == f"<p><{tag}>a&amp;b</{tag}></p>"
    assert "a&amp;b" in rich.markdown


@pytest.mark.parametrize(
    "node,expected",
    [
        (
            types.RichTextUrl(text="link", url='https://example.com/?q="&x=1'),
            '<a href="https://example.com/?q=&quot;&amp;x=1">link</a>',
        ),
        (
            types.RichTextEmailAddress(text="mail", email_address="a@b.com"),
            '<a href="mailto:a@b.com">mail</a>',
        ),
        (
            types.RichTextPhoneNumber(text="phone", phone_number="+123"),
            '<a href="tel:+123">phone</a>',
        ),
        (
            types.RichTextTextMention(text="Ada", user=types.User(id=42)),
            '<a href="tg://user?id=42">Ada</a>',
        ),
        (types.RichTextAnchor(text="", name="chapter"), '<a name="chapter"></a>'),
        (
            types.RichTextAnchorLink(text="go", anchor_name="chapter"),
            '<a href="#chapter">go</a>',
        ),
        (
            types.RichTextReference(text="note", name="n"),
            '<tg-reference name="n">note</tg-reference>',
        ),
        (
            types.RichTextReferenceLink(text="go", reference_name="n"),
            '<a href="#n">go</a>',
        ),
        (
            types.RichTextCustomEmoji(custom_emoji_id="123", alternative_text="🙂"),
            '<tg-emoji emoji-id="123">🙂</tg-emoji>',
        ),
        (
            types.RichTextMathematicalExpression(expression="x<y"),
            "<tg-math>x&lt;y</tg-math>",
        ),
    ],
)
def test_rich_inline_html_fallbacks(node, expected):
    rich = message(types.RichBlockParagraph(text=node))

    assert rich.html == "<p>" + expected + "</p>"
    assert rich.markdown == expected


def test_date_time():

    rich = message(
        types.RichBlockParagraph(
            text=types.RichTextDateTime(
                text="today",
                date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                date_time_format="D",
            )
        )
    )

    assert rich.markdown == '<tg-time unix="1767225600" format="D">today</tg-time>'


@pytest.mark.parametrize(
    "node,expected",
    [
        (types.RichBlockFooter(text="end"), "<footer>end</footer>"),
        (types.RichBlockDivider(), "<hr/>"),
        (
            types.RichBlockMathematicalExpression(expression="x<y"),
            "<tg-math-block>x&lt;y</tg-math-block>",
        ),
        (types.RichBlockAnchor(name="here"), '<a name="here"></a>'),
        (types.RichBlockThinking(text="wait"), "<tg-thinking>wait</tg-thinking>"),
        (
            types.RichBlockPullQuotation(text="quote", credit="author"),
            "<aside>quote<cite>author</cite></aside>",
        ),
        (
            types.RichBlockBlockQuotation(
                blocks=[types.RichBlockParagraph(text="quote")], credit="author"
            ),
            "<blockquote><p>quote</p><cite>author</cite></blockquote>",
        ),
    ],
)
def test_remaining_blocks(node, expected):
    assert message(node).html == expected


@pytest.mark.parametrize(
    "cls,field,scheme,tag",
    [
        (types.RichBlockPhoto, "photo", "photo", "img"),
        (types.RichBlockVideo, "video", "video", "video"),
        (types.RichBlockAnimation, "animation", "video", "video"),
        (types.RichBlockAudio, "audio", "audio", "audio"),
        (types.RichBlockVoiceNote, "voice_note", "audio", "audio"),
        (types.RichBlockDocument, "document", "document", "tg-document"),
    ],
)
def test_all_media_with_formatted_captions(cls, field, scheme, tag):
    block = cls(
        **{field: SimpleNamespace(file_id="fid")},
        caption=types.RichBlockCaption(text=types.RichTextBold(text="caption"), credit="author"),
    )
    rich = message(block)
    media = f'<{tag} src="tg://{scheme}?id=fid"' + ("/>" if tag == "img" else f"></{tag}>")

    assert (
        rich.html
        == f"<figure>{media}<figcaption><b>caption</b><cite>author</cite></figcaption></figure>"
    )
    assert rich.markdown == rich.html


def test_nested_media_dedup_and_edits_are_not_cached():
    photo = types.RichBlockPhoto(photo=SimpleNamespace(file_id="photo-id"), has_spoiler=True)
    rich = message(
        types.RichBlockList(items=[types.RichBlockListItem(label="•", blocks=[photo])]),
        types.RichBlockCollage(blocks=[photo]),
        types.RichBlockSlideshow(blocks=[photo]),
    )

    assert rich.markdown.count("tg://photo?id=photo-id") == 3
    photo.photo.file_id = "changed"

    assert "tg://photo?id=changed" in rich.to_input().html
    assert "tg-spoiler" in rich.html


def test_unordered_and_ordered_lists():
    rich = message(
        types.RichBlockList(
            items=[
                types.RichBlockListItem(
                    label="•",
                    blocks=[types.RichBlockParagraph(text="done")],
                    has_checkbox=True,
                    is_checked=True,
                )
            ]
        )
    )

    assert rich.markdown == "- [x] done"
    rich.blocks[0].items[0].value = 7
    rich.blocks[0].items[0].type = "i"

    assert '<li value="7" type="i">' in rich.markdown
    assert '<input type="checkbox" checked/>' in rich.html


def test_map_with_caption():
    rich = message(
        types.RichBlockMap(
            location=types.Location(latitude=41.9, longitude=12.5),
            zoom=14,
            width=200,
            height=100,
            caption=types.RichBlockCaption(text="Rome"),
        )
    )

    assert (
        rich.html
        == '<figure><tg-map lat="41.9" long="12.5" zoom="14"/><figcaption>Rome</figcaption></figure>'
    )


def test_warning_can_be_escalated_and_original_type_retained():

    rich = message(types.RichBlockUnsupported(original_type="PageBlockFuture"))

    with warnings.catch_warnings():
        warnings.simplefilter("error", UnsupportedRichContentWarning)

        with pytest.raises(UnsupportedRichContentWarning, match="PageBlockFuture"):
            _ = rich.html


def test_to_input_document_serializes_at_wire_level():

    rich = types.RichMessage(
        blocks=[types.RichBlockDocument(document=SimpleNamespace(file_id=DOCUMENT_ID))],
        is_rtl=True,
    )
    outgoing = write(rich.to_input())
    decoded = raw.core.TLObject.read(BytesIO(write(outgoing)))

    assert decoded.html == '<tg-document src="tg://document?id=media_1"></tg-document>'
    assert DOCUMENT_ID in rich.html
    assert decoded.rtl
    assert decoded.files[0].id == "media_1"
    assert decoded.files[0].document.id == outgoing.files[0].document.id


def test_input_photo_file_mapping():
    photo_id = "AgACAgIAAx0CAAGgr9AAAgmZX7b7IPLRl8NcV3EJkzHwI1gwT-oAAq2nMRuBpLlJPJY-URZfhTkgfeqKEAADAQADAgADeQAD_54BAAEeBA"
    result = write(types.InputRichMessage(html=f'<img src="tg://photo?id={photo_id}"/>'))

    assert isinstance(result.files[0], raw.types.InputRichFilePhoto)
    assert write(result)


def test_invalid_file_id_rejected():
    with pytest.raises(ValueError):
        write(types.InputRichMessage(html='<img src="tg://photo?id=invalid"/>'))


def test_inline_html_in_markdown_protects_literal_markdown():
    rich = message(types.RichBlockParagraph(text=types.RichTextUnderline(text="*literal*")))

    assert rich.markdown == "<u>&#42;literal&#42;</u>"
    assert rich.html == "<p><u>*literal*</u></p>"
    details = message(types.RichBlockDetails(summary="*literal*", blocks=[]))

    assert "<summary>&#42;literal&#42;</summary>" in details.markdown


def test_adjacent_styles_and_intraword_punctuation_use_html():
    rich = message(
        types.RichBlockParagraph(text=[types.RichTextBold(text="a"), types.RichTextBold(text="b")])
    )

    assert rich.markdown == "<b>a</b><b>b</b>"
    rich = message(types.RichBlockParagraph(text=["a", types.RichTextItalic(text="!"), "b"]))

    assert rich.markdown == "a<i>&#33;</i>b"


@pytest.mark.parametrize("content", ["", " ", "   "])
def test_empty_and_whitespace_code_preserve_content(content):
    rich = message(types.RichBlockParagraph(text=types.RichTextCode(text=content)))

    assert rich.markdown == f"<code>{content}</code>"


@pytest.mark.parametrize("block", [False, True])
def test_unknown_format_in_code_warns_and_preserves_text(block):
    text = types.RichTextUnsupported(original_type="TextFuture", text="x < y")
    node = (
        types.RichBlockPreformatted(text=text)
        if block
        else types.RichBlockParagraph(text=types.RichTextCode(text=text))
    )

    with pytest.warns(UserWarning, match="TextFuture"):
        assert "x &lt; y" in message(node).html


def test_unknown_list_item_warns_with_its_original_type():

    class PageListItemFuture:
        pass

    parsed = asyncio.run(types.RichBlockListItem._parse_list_item(None, PageListItemFuture()))
    rich = message(types.RichBlockList(items=[parsed]))

    with pytest.warns(UserWarning, match="PageListItemFuture"):
        assert rich.html == ""


@pytest.mark.parametrize("content", ["    hello", "\thello", ""])
def test_indentation_and_empty_paragraphs_remain_paragraphs(content):
    assert message(types.RichBlockParagraph(text=content)).markdown == f"<p>{content}</p>"


def write(value):
    if isinstance(value, types.InputRichMessage):

        async def run():
            return await value.write(client=None)

        return asyncio.run(run())

    return value.write()


def test_compact_table_flag_is_preserved():
    rich = message(
        types.RichBlockTable(
            cells=[[types.RichBlockTableCell(text="A", is_header=True)]], is_compact=True
        )
    )

    assert rich.html == "<table compact><tr><th>A</th></tr></table>"
    assert rich.markdown == rich.html
