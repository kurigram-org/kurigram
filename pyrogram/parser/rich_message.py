"""Serialize rich message trees using Telegram's rich formatting dialects.

HTML fallbacks deliberately render their children as HTML too: Markdown is not
parsed inside most block HTML elements by Telegram.
"""

import re
import warnings
from html import escape

from pyrogram import enums, types, utils


class UnsupportedRichContentWarning(UserWarning):
    """An unsupported rich node was skipped or its formatting was discarded."""


def _tag(tag_name, content=None, **attributes):
    attrs = "".join(
        " "
        + key.replace("_", "-")
        + ("" if value is True else '="' + escape(str(value), quote=True) + '"')
        for key, value in attributes.items()
        if value is not None and value is not False
    )

    return (
        f"<{tag_name}{attrs}/>" if content is None else f"<{tag_name}{attrs}>{content}</{tag_name}>"
    )


def _literal(text, html):
    text = escape(text, quote=False)

    if html:
        if html == "inline":
            # Numeric entities protect literals when Telegram parses Markdown
            # inside inline HTML. Backslashes would be visible in HTML mode.
            text = re.sub(r"([\\`*_{}\[\]()#+.!|~=$^-])", lambda m: f"&#{ord(m[0])};", text)

        return text.replace("\n", "<br>")

    # Escape punctuation even at line starts, where it may introduce a block.
    return re.sub(r"([\\`*_{}\[\]()#+.!|~=$^-])", r"\\\1", text).replace("\n", "<br>")


class RichMessageSerializer:
    """Serialize a tree with reusable file IDs embedded in media links."""

    @staticmethod
    def _warn(node, path, reason=None):
        name = getattr(node, "original_type", None) or type(node).__name__
        warnings.warn(
            f"Unsupported rich content {name} at {path}; "
            f"{reason or 'skipping unsupported content or formatting'}; content={node!r}",
            UnsupportedRichContentWarning,
            stacklevel=4,
        )

    def render(self, message, html):
        return self.blocks(message.blocks, html, "blocks")

    def blocks(self, blocks, html, path):
        rendered = [self.block(block, html, f"{path}[{i}]") for i, block in enumerate(blocks)]

        return ("\n" if html else "\n\n").join(part for part in rendered if part)

    def plain_text(self, node, path):
        # Validate/warn through the same dispatcher before dropping formatting.
        # Code blocks still need to report unknown wrappers inside their text.
        self.text(node, True, path)

        return types.RichText._to_plain_text(node)

    def text(self, node, html, path):
        if node is None:
            return ""

        if isinstance(node, str):
            return _literal(node, html)

        if isinstance(node, (list, tuple)):
            parts = []

            for i, value in enumerate(node):
                mode = html

                if not html and not isinstance(value, str):
                    before = types.RichText._to_plain_text(node[i - 1]) if i else ""
                    after = types.RichText._to_plain_text(node[i + 1]) if i + 1 < len(node) else ""

                    if (before and not before[-1].isspace()) or (after and not after[0].isspace()):
                        mode = "inline"

                parts.append(self.text(value, mode, f"{path}[{i}]"))

            return "".join(parts)

        inline_mode = html or "inline"
        kind = type(node)
        styles = {
            types.RichTextBold: ("b", "**"),
            types.RichTextItalic: ("i", "*"),
            types.RichTextUnderline: ("u", None),
            types.RichTextStrikethrough: ("s", "~~"),
            types.RichTextSpoiler: ("tg-spoiler", "||"),
            types.RichTextMarked: ("mark", "=="),
            types.RichTextSubscript: ("sub", None),
            types.RichTextSuperscript: ("sup", None),
        }

        if kind in styles:
            tag, delimiter = styles[kind]
            content = self.text(
                node.text, (inline_mode if delimiter is None else html), path + ".text"
            )

            if html or delimiter is None:
                return _tag(tag, content)

            # Delimiters cannot open/close next to whitespace. Use HTML when
            # nesting the same delimiter would make the syntax ambiguous.
            if not content or content != content.strip() or delimiter in content:
                return _tag(tag, self.text(node.text, inline_mode, path + ".text"))

            return delimiter + content + delimiter

        if kind is types.RichTextCode:
            content = self.plain_text(node.text, path + ".text")

            if html or not content.strip() or "\n" in content:
                return _tag("code", escape(content, quote=False))

            fence = "`" * (max([len(m) for m in re.findall(r"`+", content)] or [0]) + 1)
            padding = " " if content.startswith(("`", " ")) or content.endswith(("`", " ")) else ""

            return fence + padding + content + padding + fence

        if kind is types.RichTextMathematicalExpression:
            return _tag("tg-math", escape(node.expression, quote=False))

        if kind is types.RichTextCustomEmoji:
            return _tag(
                "tg-emoji",
                _literal(node.alternative_text, inline_mode),
                emoji_id=node.custom_emoji_id,
            )

        if kind is types.RichTextDateTime:
            return _tag(
                "tg-time",
                self.text(node.text, inline_mode, path + ".text"),
                unix=utils.datetime_to_timestamp(node.date),
                format=node.date_time_format,
            )

        if kind is types.RichTextButton:
            return self.button(node.button, inline_mode, path + ".button")

        if kind is types.RichTextAnchor:
            return _tag("a", "", name=node.name) + self.text(node.text, html, path + ".text")

        if kind is types.RichTextReference:
            return _tag(
                "tg-reference",
                self.text(node.text, inline_mode, path + ".text"),
                name=node.name,
            )

        links = {
            types.RichTextUrl: ("url", ""),
            types.RichTextEmailAddress: ("email_address", "mailto:"),
            types.RichTextPhoneNumber: ("phone_number", "tel:"),
            types.RichTextAnchorLink: ("anchor_name", "#"),
            types.RichTextReferenceLink: ("reference_name", "#"),
        }

        if kind in links or kind is types.RichTextTextMention:
            if kind is types.RichTextTextMention:
                url = f"tg://user?id={node.user.id}"
            else:
                field, prefix = links[kind]
                url = prefix + getattr(node, field)

            # HTML avoids ambiguous parentheses and quotes in Markdown links.
            return _tag("a", self.text(node.text, inline_mode, path + ".text"), href=url)

        if kind in (
            types.RichTextMention,
            types.RichTextHashtag,
            types.RichTextCashtag,
            types.RichTextBotCommand,
            types.RichTextBankCardNumber,
        ):
            return self.text(node.text, html, path + ".text")

        self._warn(node, path)

        return self.text(getattr(node, "text", None), html, path + ".text")

    def button(self, node, html, path):
        content = self.text(node.text, html, path + ".text")
        actions = (
            "url",
            "callback_data",
            "web_app",
            "login_url",
            "switch_inline_query",
            "switch_inline_query_current_chat",
            "switch_inline_query_chosen_chat",
            "copy_text",
            "disabled",
        )
        selected = [field for field in actions if getattr(node, field) is not None]

        if len(selected) != 1:
            self._warn(node, path, "expected exactly one button action; retaining its text")

            return content

        action = selected[0]
        value = getattr(node, action)
        attributes = {"type": action}

        if node.style not in (None, enums.ButtonStyle.DEFAULT):
            attributes["style"] = node.style.value

        if action == "url":
            attributes["url"] = value
        elif action == "callback_data":
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8")
                except UnicodeDecodeError:
                    self._warn(
                        node,
                        path,
                        "callback data is not UTF-8 and cannot be represented in HTML/Markdown; "
                        "use blocks to preserve binary data; retaining its text",
                    )

                    return content

            attributes["data"] = value
        elif action == "web_app":
            attributes["url"] = value.url
        elif action == "login_url":
            attributes.update(
                url=value.url,
                forward_text=value.forward_text,
                request_write_access=value.request_write_access,
            )

            if value.bot_username:
                self._warn(
                    node,
                    path,
                    "HTML/Markdown login buttons use the sending bot; "
                    "use blocks to preserve bot_username; retaining its text",
                )

                return content
        elif action in ("switch_inline_query", "switch_inline_query_current_chat"):
            attributes["query"] = value
        elif action == "switch_inline_query_chosen_chat":
            attributes.update(
                query=value.query or "",
                allow_user_chats=value.allow_user_chats,
                allow_bot_chats=value.allow_bot_chats,
                allow_group_chats=value.allow_group_chats,
                allow_channel_chats=value.allow_channel_chats,
            )
        elif action == "copy_text":
            attributes["text"] = value.text

        return _tag("tg-button", content, **attributes)

    def caption(self, node, path, tag="figcaption"):
        if node is None:
            return ""

        # Accept older RichBlockTable objects whose caption was a RichText.
        if isinstance(node, types.RichBlockCaption):
            content = self.text(node.text, True, path + ".text")

            if node.credit is not None:
                content += _tag("cite", self.text(node.credit, True, path + ".credit"))
        else:
            content = self.text(node, True, path)

        return _tag(tag, content)

    def block(self, node, html, path):
        kind = type(node)

        if kind is types.RichBlockParagraph:
            content = self.text(node.text, html, path + ".text")

            if not html and (not content or content.startswith((" ", "\t"))):
                return _tag("p", self.text(node.text, True, path + ".text"))

            return _tag("p", content) if html else content

        if kind is types.RichBlockSectionHeading:
            if node.size not in range(1, 7):
                raise ValueError("Rich heading size must be between 1 and 6")

            content = self.text(node.text, html, path + ".text")

            return _tag(f"h{node.size}", content) if html else "#" * node.size + " " + content

        if kind is types.RichBlockDivider:
            return "<hr/>" if html else "---"

        if kind is types.RichBlockPreformatted:
            content = self.plain_text(node.text, path + ".text")
            language = node.language or ""

            if html or any(c in language for c in "`\r\n"):
                code = escape(content, quote=False)

                if language:
                    code = _tag("code", code, **{"class": "language-" + language})

                return _tag("pre", code)

            fence = "`" * max([3, *(len(m) + 1 for m in re.findall(r"`+", content))])

            return f"{fence}{language}\n{content}\n{fence}"

        if kind is types.RichBlockAnchor:
            return _tag("a", "", name=node.name)

        if kind is types.RichBlockMathematicalExpression:
            return _tag("tg-math-block", escape(node.expression, quote=False))

        if kind in (types.RichBlockFooter, types.RichBlockThinking):
            return _tag(
                "footer" if kind is types.RichBlockFooter else "tg-thinking",
                self.text(node.text, True, path + ".text"),
            )

        if kind is types.RichBlockBlockQuotation:
            if not html and node.credit is None:
                content = self.blocks(node.blocks, False, path + ".blocks")

                return "\n".join("> " + line for line in content.split("\n")) if content else ""

            content = self.blocks(node.blocks, True, path + ".blocks")

            if node.credit is not None:
                content += _tag("cite", self.text(node.credit, True, path + ".credit"))

            return _tag("blockquote", content)

        if kind is types.RichBlockButtons:
            content = "".join(
                self.button(button, True, f"{path}.buttons[{i}]")
                for i, button in enumerate(node.buttons)
            )

            return _tag("tg-button-row", content, align=node.align)

        if kind is types.RichBlockExpandableBlockQuotation:
            content = self.text(node.text, True, path + ".text")

            if node.credit is not None:
                content += _tag("cite", self.text(node.credit, True, path + ".credit"))

            return _tag("blockquote", content, expandable=True)

        if kind is types.RichBlockPullQuotation:
            content = self.text(node.text, True, path + ".text")

            if node.credit is not None:
                content += _tag("cite", self.text(node.credit, True, path + ".credit"))

            return _tag("aside", content)

        if kind is types.RichBlockDetails:
            content = _tag("summary", self.text(node.summary, html or "inline", path + ".summary"))
            content += self.blocks(node.blocks, True, path + ".blocks")

            return _tag("details", content, open=node.is_open)

        if kind in (types.RichBlockCollage, types.RichBlockSlideshow):
            content = self.blocks(node.blocks, True, path + ".blocks")
            content += self.caption(node.caption, path + ".caption")

            return _tag(
                "tg-collage" if kind is types.RichBlockCollage else "tg-slideshow",
                content,
            )

        if kind is types.RichBlockList:
            return self.list_block(node, html, path)

        if kind is types.RichBlockTable:
            return self.table(node, html, path)

        if kind is types.RichBlockMap:
            content = _tag(
                "tg-map",
                lat=node.location.latitude,
                long=node.location.longitude,
                zoom=node.zoom,
            )

            return (
                _tag("figure", content + self.caption(node.caption, path + ".caption"))
                if node.caption
                else content
            )

        media_types = {
            types.RichBlockPhoto: ("photo", "photo", "img"),
            types.RichBlockVideo: ("video", "video", "video"),
            types.RichBlockAnimation: ("animation", "video", "video"),
            types.RichBlockAudio: ("audio", "audio", "audio"),
            types.RichBlockVoiceNote: ("voice_note", "audio", "audio"),
            types.RichBlockDocument: ("document", "document", "tg-document"),
        }

        if kind in media_types:
            field, scheme, tag = media_types[kind]
            file_id = getattr(node, field).file_id
            src = f"tg://{scheme}?id={file_id}"
            spoiler = getattr(node, "has_spoiler", None)

            if not html and not node.caption and not spoiler:
                return f"![]({src})"

            content = _tag(tag, None if tag == "img" else "", src=src, tg_spoiler=spoiler)

            return (
                _tag("figure", content + self.caption(node.caption, path + ".caption"))
                if node.caption
                else content
            )

        self._warn(node, path)

        return ""

    def list_block(self, node, html, path):
        if not node.items:
            return ""

        def ordered(item):
            return (
                item.value is not None
                or item.type is not None
                or item.label not in ("•", "-", "*", "+")
            )

        simple = all(
            type(item) is types.RichBlockListItem
            and not ordered(item)
            and len(item.blocks) == 1
            and type(item.blocks[0]) is types.RichBlockParagraph
            for item in node.items
        )

        if not html and simple:
            result = []

            for i, item in enumerate(node.items):
                prefix = (
                    "- " + ("[x] " if item.is_checked else "[ ] ") if item.has_checkbox else "- "
                )
                result.append(
                    prefix + self.block(item.blocks[0], False, f"{path}.items[{i}].blocks[0]")
                )

            return "\n".join(result)

        # Group consecutive items by list kind, preserving ordered item values/types.
        groups = []
        current = []
        previous = None

        for i, item in enumerate(node.items):
            item_path = f"{path}.items[{i}]"

            if type(item) is not types.RichBlockListItem:
                self._warn(item, item_path)
                continue

            is_ordered = ordered(item)

            if previous is not None and previous != is_ordered:
                groups.append(_tag("ol" if previous else "ul", "".join(current)))
                current = []

            content = self.blocks(item.blocks, True, item_path + ".blocks")

            if item.has_checkbox:
                content = _tag("input", type="checkbox", checked=item.is_checked) + content

            value = item.value

            if is_ordered and value is None and item.label.rstrip(".").isdigit():
                value = int(item.label.rstrip("."))

            current.append(_tag("li", content, value=value if is_ordered else None, type=item.type))
            previous = is_ordered

        if current:
            groups.append(_tag("ol" if previous else "ul", "".join(current)))

        return "".join(groups)

    def table(self, node, html, path):
        rows = node.cells
        simple = bool(rows and rows[0]) and not (
            node.caption or node.is_bordered or node.is_striped or node.is_compact
        )
        simple = simple and all(len(row) == len(rows[0]) for row in rows)
        simple = simple and all(
            type(cell) is types.RichBlockTableCell
            and cell.text is not None
            and (cell.colspan or 1) == 1
            and (cell.rowspan or 1) == 1
            and cell.valign in (None, "top")
            and bool(cell.is_header) == (r == 0)
            and (cell.align or "left") == (rows[0][c].align or "left")
            for r, row in enumerate(rows)
            for c, cell in enumerate(row)
        )

        if not html and simple:
            lines = []

            for r, row in enumerate(rows):
                # Inline HTML in cells safely handles pipes in code/links too.
                values = [
                    self.text(cell.text, False, f"{path}.cells[{r}][{c}].text")
                    for c, cell in enumerate(row)
                ]

                if any("|" in value.replace("\\|", "") or "\n" in value for value in values):
                    return self.table(node, True, path)

                lines.append("| " + " | ".join(values) + " |")

                if r == 0:
                    lines.append(
                        "| "
                        + " | ".join(
                            {"left": ":---", "center": ":---:", "right": "---:"}[
                                cell.align or "left"
                            ]
                            for cell in row
                        )
                        + " |"
                    )

            return "\n".join(lines)

        content = self.caption(node.caption, path + ".caption", "caption")

        for r, row in enumerate(rows):
            cells = []

            for c, cell in enumerate(row):
                cell_path = f"{path}.cells[{r}][{c}]"

                if type(cell) is not types.RichBlockTableCell:
                    self._warn(cell, cell_path)
                    continue

                if cell.text is None:
                    continue

                cells.append(
                    _tag(
                        "th" if cell.is_header else "td",
                        self.text(cell.text, True, cell_path + ".text"),
                        colspan=cell.colspan if (cell.colspan or 1) > 1 else None,
                        rowspan=cell.rowspan if (cell.rowspan or 1) > 1 else None,
                        align=cell.align,
                        valign=cell.valign,
                    )
                )

            content += _tag("tr", "".join(cells))

        return _tag(
            "table",
            content,
            bordered=node.is_bordered,
            striped=node.is_striped,
            compact=node.is_compact,
        )
