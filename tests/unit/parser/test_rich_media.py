import asyncio
from io import BytesIO
from types import SimpleNamespace

import pytest

from pyrogram import raw, types
from pyrogram.parser.rich_media import _HTMLMedia

FID = "BQACAgIAAx0CAAGgr9AAAgmPX7b4UxbjNoFEO_L0I4s6wrXNJA8AAgQAA4GkuUm9FFvIaOhXWR4E"
URL = "tg://document?id=" + FID


@pytest.mark.parametrize(
    "format,content",
    [
        ("html", '<tg-document src="' + URL + '"></tg-document>'),
        ("markdown", "![](" + URL + ")"),
        ("markdown", '<figure><tg-document src="' + URL + '"></tg-document></figure>'),
    ],
)
def test_embedded_file_id_is_resolved_at_write(format, content):
    outgoing = types.InputRichMessage(**{format: content})
    result = write(outgoing)

    assert len(result.files) == 1
    assert result.files[0].document.id == 5312458109417947140
    assert FID not in getattr(result, format)
    assert "tg://document?id=" + result.files[0].id in getattr(result, format)
    assert getattr(outgoing, format) == content
    assert write(write(outgoing)) == write(result)


def test_repeated_file_ids_deduplicate():
    text = "![](" + URL + ")\n\n![](" + URL + ")"
    result = write(types.InputRichMessage(markdown=text))

    assert len(result.files) == 1
    assert result.markdown.count("tg://document?id=media_1") == 2


@pytest.mark.parametrize(
    "format,content",
    [
        ("html", "<pre><code>![](" + URL + ")</code></pre>"),
        ("html", '<!-- <tg-document src="' + URL + '"></tg-document> -->'),
        ("html", '<a href="' + URL + '">link</a>'),
        ("markdown", "`![](" + URL + ")`"),
        ("markdown", '```html\n<tg-document src="' + URL + '"></tg-document>\n```'),
        ("markdown", "~~~\n![](" + URL + ")\n~~~"),
        ("markdown", "    ![](" + URL + ")"),
        ("markdown", "\\![](" + URL + ")"),
        ("markdown", "<code>![](" + URL + ")</code>"),
    ],
)
def test_literal_urls_are_not_rewritten(format, content):
    result = write(types.InputRichMessage(**{format: content}))

    assert result.files is None
    assert getattr(result, format) == content


def test_urls_and_emoji_are_left_alone():
    content = "![](https://example.com/a.png)\n\n![🙂](tg://emoji?id=123)"
    result = write(types.InputRichMessage(markdown=content))

    assert result.files is None
    assert result.markdown == content


def test_photo_url_rejects_document_file_id():
    with pytest.raises(ValueError, match="photo"):
        write(types.InputRichMessage(markdown="![](tg://photo?id=" + FID + ")"))


def test_generated_blockquote_code_is_not_media():
    rich = types.RichMessage(
        blocks=[
            types.RichBlockBlockQuotation(
                blocks=[types.RichBlockPreformatted(text="![](" + URL + ")")]
            )
        ]
    )
    result = write(types.InputRichMessage(markdown=rich.markdown))

    assert result.files is None
    assert result.markdown == rich.markdown


def test_escaped_backtick_does_not_hide_real_media():
    text = "\\`literal\n\n![](" + URL + ")\n\n\\`"
    result = write(types.InputRichMessage(markdown=text))

    assert len(result.files) == 1


def test_html_attribute_entities_and_unicode_offsets():
    text = 'שלום\n<tg-document src="tg://document?id&#61;' + FID + '"></tg-document>'
    result = write(types.InputRichMessage(html=text))

    assert result.html == 'שלום\n<tg-document src="tg://document?id=media_1"></tg-document>'
    assert len(result.files) == 1


def test_backticks_inside_html_blocks_do_not_hide_media():
    rich = types.RichMessage(
        blocks=[
            types.RichBlockFooter(text="`"),
            types.RichBlockDocument(document=type("Document", (), {"file_id": FID})()),
            types.RichBlockFooter(text="`"),
        ]
    )

    assert len(write(rich.to_input(format="markdown")).files) == 1


def test_unclosed_backtick_does_not_cross_paragraphs():
    text = "`\n\n![](" + URL + ")\n\n`"

    assert len(write(types.InputRichMessage(markdown=text)).files) == 1


@pytest.mark.parametrize(
    "text",
    [
        '    <tg-document src="' + URL + '"></tg-document>',
        '\\<tg-document src="' + URL + '"></tg-document>',
        "> ~~~\n> ![](" + URL + ")\n> ~~~",
    ],
)
def test_additional_literal_media_contexts(text):
    result = write(types.InputRichMessage(markdown=text))

    assert result.files is None
    assert result.markdown == text


@pytest.mark.parametrize(
    "scheme,file_id",
    [
        (
            "photo",
            "AgACAgIAAx0CAAGgr9AAAgmZX7b7IPLRl8NcV3EJkzHwI1gwT-oAAq2nMRuBpLlJPJY-URZfhTkgfeqKEAADAQADAgADeQAD_54BAAEeBA",
        ),
        (
            "video",
            "BAACAgIAAx0CAAGgr9AAAgmRX7b4Xv9f-4BK5VR_5ppIOF6UIp0AAgYAA4GkuUmhnZz2xC37wR4E",
        ),
        (
            "video",
            "CgACAgIAAx0CAAGgr9AAAgmSX7b4Y2g8_QW2XFd49iUmRnHOyG8AAgcAA4GkuUnry9gWDzF_5R4E",
        ),
        (
            "audio",
            "CQACAgIAAx0CAAGgr9AAAgmQX7b4XPBstC1fFUuJBooHTHFd7HMAAgUAA4GkuUnVOGG5P196yR4E",
        ),
        (
            "audio",
            "AwACAgIAAx0CAAGgr9AAAgmUX7b4c1KQyHVwzffxC2EnSYWsMAQAAgkAA4GkuUlsZUZ4_I97AR4E",
        ),
    ],
)
def test_embedded_media_kinds_produce_serializable_files(scheme, file_id):

    outgoing = write(types.InputRichMessage(markdown=f"![](tg://{scheme}?id={file_id})"))
    decoded = raw.core.TLObject.read(BytesIO(write(outgoing)))

    assert len(decoded.files) == 1
    assert decoded.markdown == f"![](tg://{scheme}?id=media_1)"
    assert isinstance(
        decoded.files[0],
        raw.types.InputRichFilePhoto if scheme == "photo" else raw.types.InputRichFileDocument,
    )


def test_html_examples_in_separate_fences_cannot_capture_real_media():

    rich = types.RichMessage(
        blocks=[
            types.RichBlockPreformatted(text="<p>"),
            types.RichBlockDocument(document=SimpleNamespace(file_id=FID)),
            types.RichBlockPreformatted(text="</p>"),
        ]
    )
    result = write(rich.to_input(format="markdown"))

    assert len(result.files) == 1
    assert "```\n<p>\n```" in result.markdown
    assert "```\n</p>\n```" in result.markdown


def test_html_examples_in_separate_inline_code_cannot_capture_real_media():

    rich = types.RichMessage(
        blocks=[
            types.RichBlockParagraph(text=types.RichTextCode(text="<p>")),
            types.RichBlockDocument(document=SimpleNamespace(file_id=FID)),
            types.RichBlockParagraph(text=types.RichTextCode(text="</p>")),
        ]
    )

    assert len(write(rich.to_input(format="markdown")).files) == 1


def test_backticks_in_html_captions_do_not_hide_sibling_media():

    rich = types.RichMessage(
        blocks=[
            types.RichBlockCollage(
                blocks=[
                    types.RichBlockDocument(
                        document=SimpleNamespace(file_id=FID),
                        caption=types.RichBlockCaption(text="`"),
                    ),
                    types.RichBlockDocument(
                        document=SimpleNamespace(file_id=FID),
                        caption=types.RichBlockCaption(text="`"),
                    ),
                ]
            )
        ]
    )
    result = write(rich.to_input(format="markdown"))

    assert result.markdown.count("tg://document?id=media_1") == 2


def write(value):
    if isinstance(value, types.InputRichMessage):

        async def run():
            return await value.write(client=None)

        return asyncio.run(run())

    return value.write()


def test_embedded_ids_coexist_with_original_upload_aliases():
    result = write(
        types.InputRichMessage(
            markdown="![](tg://document?id=media_2)\n\n![](" + URL + ")",
            media=[types.InputRichMessageMedia(id="media_2", media=types.InputMediaDocument(FID))],
        )
    )

    assert [item.id for item in result.files] == ["media_2", "media_3"]
    assert result.markdown == "![](tg://document?id=media_2)\n\n![](tg://document?id=media_3)"


def test_multiple_embedded_files_avoid_existing_and_generated_aliases():
    other_id = "BAACAgIAAx0CAAGgr9AAAgmRX7b4Xv9f-4BK5VR_5ppIOF6UIp0AAgYAA4GkuUmhnZz2xC37wR4E"
    result = write(
        types.InputRichMessage(
            markdown=f"![]({URL})\n\n![](tg://video?id={other_id})",
            media=[types.InputRichMessageMedia(id="media_2", media=types.InputMediaDocument(FID))],
        )
    )

    assert [item.id for item in result.files] == ["media_2", "media_3", "media_4"]


@pytest.mark.parametrize("tag", ["tg-button-row", "tg-button"])
def test_button_labels_do_not_resolve_literal_media_links(tag):
    content = f"<{tag}>![example]({URL})</{tag}>"
    result = write(types.InputRichMessage(markdown=content))

    assert result.markdown == content
    assert result.files is None


def test_missing_start_tag_text_does_not_create_media_spans():
    parser = _HTMLMedia("")
    parser.handle_starttag("img", [])

    assert parser.spans == []
    assert parser.urls == []
