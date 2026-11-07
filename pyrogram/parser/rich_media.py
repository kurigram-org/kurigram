"""Resolve embedded reusable file IDs only at media positions, before sending."""

import re
from html import unescape
from html.parser import HTMLParser

from pyrogram import raw, utils

_URL = re.compile(r"tg://(photo|video|audio|document)\?id=([A-Za-z0-9_-]+)\Z")
_ATTR = re.compile(r"""([^\s=<>/]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""")
_IMAGE = re.compile(
    r"!\[(?:\\.|[^\]\\])*\]\(\s*<?(tg://(?:photo|video|audio|document)\?id=[A-Za-z0-9_-]+)>?(?=[\s)])"
)


def _mask(source, spans):
    chars = list(source)

    for start, end in spans:
        for i in range(start, end):
            if chars[i] != "\n":
                chars[i] = " "

    return "".join(chars)


def _markdown_code(source, inline=True):
    spans = []
    fence = None
    offset = 0

    for line in source.splitlines(keepends=True):
        body = re.sub(r"^(?: {0,3}>[ \t]?)+", "", line)
        opening = re.match(r" {0,3}(`{3,}|~{3,})(.*)", body)

        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*", body):
                spans.append((fence[2], offset + len(line)))
                fence = None
        elif opening:
            fence = (opening[1][0], len(opening[1]), offset)
        elif line.strip() and line.startswith(("    ", "\t")):
            spans.append((offset, offset + len(line)))

        offset += len(line)

    if fence:
        spans.append((fence[2], len(source)))

    if not inline:
        return spans

    masked = _mask(source, spans)
    # A code span closes only on a run with the same number of backticks.
    runs = list(re.finditer(r"`+", masked))
    i = 0

    while i < len(runs):
        opening = runs[i]
        before = masked[: opening.start()]

        if (len(before) - len(before.rstrip("\\"))) % 2:
            i += 1
            continue

        j = next(
            (
                j
                for j in range(i + 1, len(runs))
                if len(runs[j][0]) == len(opening[0])
                and not re.search(r"\n[ \t]*\n", masked[opening.end() : runs[j].start()])
            ),
            None,
        )

        if j is None:
            i += 1
        else:
            spans.append((opening.start(), runs[j].end()))
            i = j + 1

    return spans


class _HTMLMedia(HTMLParser):
    def __init__(self, source, markdown=False):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.markdown = markdown
        self.offsets = [0]
        self.offsets.extend(m.end() for m in re.finditer("\n", source))
        self.urls = []
        self.spans = []
        self.containers = []

    def _position(self):
        line, column = self.getpos()

        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self._position()
        text = self.get_starttag_text()

        if text is None:
            return

        self.spans.append((start, start + len(text)))
        before = self.source[:start]

        if self.markdown and not self.containers and (len(before) - len(before.rstrip("\\"))) % 2:
            return

        literal = any(
            t in ("code", "pre", "tg-button", "tg-button-row") for t, _ in self.containers
        )

        if tag in ("img", "video", "audio", "tg-document") and not literal:
            for attr in _ATTR.finditer(text):
                if attr[1].lower() == "src":
                    group = next(g for g in (2, 3, 4) if attr[g] is not None)

                    if _URL.fullmatch(unescape(attr[group])):
                        self.urls.append(
                            (
                                start + attr.start(group),
                                start + attr.end(group),
                                unescape(attr[group]),
                            )
                        )

        if tag in (
            "code",
            "pre",
            "p",
            "table",
            "ul",
            "ol",
            "blockquote",
            "aside",
            "figure",
            "figcaption",
            "footer",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "tg-math-block",
            "tg-thinking",
            "tg-button",
            "tg-button-row",
            "script",
            "style",
        ):
            self.containers.append((tag, start))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.containers) - 1, -1, -1):
            if self.containers[i][0] == tag:
                _, start = self.containers[i]
                end = self.source.find(">", self._position()) + 1
                self.spans.append((start, end))
                del self.containers[i:]
                break

    def handle_comment(self, data):
        start = self._position()
        end = self.source.find("-->", start)
        self.spans.append((start, end + 3 if end >= 0 else len(self.source)))


def resolve_media(content, html, existing_files=None):
    """Return rewritten text and raw files without mutating the caller's input.

    Media URLs embed file IDs; short aliases exist only in the raw payload.
    Literal examples in code/comments and ordinary hyperlinks are not media.
    """
    if html:
        code = []
    else:
        # The region which opens first owns its contents: a code span can
        # contain literal HTML, while an HTML block/attribute can contain
        # literal backticks. Resolve precedence before masking either kind.
        fences = _markdown_code(content, inline=False)
        visible = _mask(content, fences)
        preliminary = _HTMLMedia(visible, markdown=True)
        preliminary.feed(visible)
        preliminary.close()
        candidates = _markdown_code(visible)
        regions = [(start, end, False) for start, end in preliminary.spans]
        regions.extend((start, end, True) for start, end in candidates)
        regions.sort(key=lambda region: (region[0], -region[1]))
        code = list(fences)
        covered_until = 0

        for start, end, is_code in regions:
            if start < covered_until:
                continue

            covered_until = end

            if is_code:
                code.append((start, end))

    parser = _HTMLMedia(_mask(content, code), markdown=not html)
    parser.feed(parser.source)
    parser.close()
    urls = parser.urls

    if not html:
        spans = code + parser.spans + [(start, len(content)) for _, start in parser.containers]
        masked = _mask(content, spans)

        for match in _IMAGE.finditer(masked):
            before = masked[: match.start()]

            if (len(before) - len(before.rstrip("\\"))) % 2:
                continue

            urls.append((match.start(1), match.end(1), match[1]))

    resolved = {}
    replacements = []
    files = list(existing_files or [])
    aliases = {file.id for file in files}
    reserved_aliases = set(aliases)

    for start, end, url in sorted(urls):
        scheme, file_id = _URL.fullmatch(url).groups()

        if file_id in aliases:
            continue

        if file_id not in resolved:
            item = utils.get_input_media_from_file_id(file_id)
            index = len(files) + 1

            while f"media_{index}" in reserved_aliases:
                index += 1

            alias = f"media_{index}"
            reserved_aliases.add(alias)
            resolved[file_id] = alias, item

            if isinstance(item, raw.types.InputMediaPhoto):
                files.append(raw.types.InputRichFilePhoto(id=alias, photo=item.id))
            else:
                files.append(raw.types.InputRichFileDocument(id=alias, document=item.id))

        alias, item = resolved[file_id]

        if (scheme == "photo") != isinstance(item, raw.types.InputMediaPhoto):
            raise ValueError(f"File ID does not match rich media scheme {scheme}")

        replacements.append((start, end, f"tg://{scheme}?id={alias}"))

    for start, end, url in reversed(replacements):
        content = content[:start] + url + content[end:]

    return content, files or None
