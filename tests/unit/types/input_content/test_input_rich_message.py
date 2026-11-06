#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations

from typing import Final

import pytest

from pyrogram import raw, types
from pyrogram.file_id import FileId, FileType, ThumbnailSource

_PHOTO_FILE_ID: Final[str] = FileId(
    file_type=FileType.PHOTO,
    dc_id=2,
    media_id=333,
    access_hash=444,
    file_reference=b"ref",
    thumbnail_source=ThumbnailSource.THUMBNAIL,
    thumbnail_file_type=FileType.PHOTO,
    thumbnail_size="x",
    volume_id=0,
    local_id=0,
).encode()

_VOICE_FILE_ID: Final[str] = FileId(
    file_type=FileType.VOICE,
    dc_id=2,
    media_id=111,
    access_hash=222,
    file_reference=b"ref",
).encode()


class _PeerResolver:
    """Answers `resolve_peer` like a client with a warm peer storage."""

    async def resolve_peer(self, peer_id: int) -> raw.types.InputPeerUser:
        return raw.types.InputPeerUser(
            user_id=peer_id,
            access_hash=777,
        )


async def test_a_blocks_message_collects_its_mentioned_users() -> None:
    mention = types.RichTextTextMention(
        text="Dan",
        user=types.User(
            id=12345,
            first_name="Dan",
        ),
    )
    message = types.InputRichMessage(
        blocks=[types.InputRichBlockParagraph(text=mention)],
        is_rtl=True,
    )

    result = await message.write(client=_PeerResolver())

    assert result == raw.types.InputRichMessage(
        rtl=True,
        noautolink=None,
        blocks=[
            raw.types.PageBlockParagraph(
                text=raw.types.TextMentionName(
                    text=raw.types.TextPlain(text="Dan"),
                    user_id=12345,
                ),
            ),
        ],
        photos=None,
        documents=None,
        users=[
            raw.types.InputUser(
                user_id=12345,
                access_hash=777,
            ),
        ],
    )


class _FixedPeerResolver:
    """Answers `resolve_peer` with one fixed peer."""

    def __init__(self, peer: raw.base.InputPeer) -> None:
        self.peer = peer

    async def resolve_peer(self, peer_id: int) -> raw.base.InputPeer:
        return self.peer


_SEEN_IN: Final = raw.types.InputPeerChannel(channel_id=5, access_hash=55)


@pytest.mark.parametrize(
    ("peer", "expected"),
    [
        (
            raw.types.InputPeerUser(user_id=12345, access_hash=777),
            raw.types.InputUser(user_id=12345, access_hash=777),
        ),
        # A `min` user has no `access_hash` to read: `resolve_peer` addresses it through a
        #  message it was seen in, and reading `.access_hash` off that crashed.
        (
            raw.types.InputPeerUserFromMessage(peer=_SEEN_IN, msg_id=3, user_id=12345),
            raw.types.InputUserFromMessage(peer=_SEEN_IN, msg_id=3, user_id=12345),
        ),
    ],
)
async def test_a_mentioned_user_is_sent_as_an_input_user(
    peer: raw.base.InputPeer, expected: raw.base.InputUser
) -> None:
    mention = types.RichTextTextMention(text="Dan", user=types.User(id=12345, first_name="Dan"))
    message = types.InputRichMessage(blocks=[types.InputRichBlockParagraph(text=mention)])

    result = await message.write(client=_FixedPeerResolver(peer))

    assert isinstance(result, raw.types.InputRichMessage)
    assert result.users is not None
    (user,) = result.users
    # Compared as bytes: `TLObject.__eq__` looks at the fields only, so the `InputPeer` itself
    #  would pass for the `InputUser` the field needs.
    assert user.write() == expected.write()


async def test_a_blocks_message_carries_its_collected_photos() -> None:
    message = types.InputRichMessage(
        blocks=[
            types.InputRichBlockPhoto(photo=types.InputMediaPhoto(_PHOTO_FILE_ID)),
        ],
    )

    result = await message.write(client=None)

    assert result.photos == [
        raw.types.InputPhoto(
            id=333,
            access_hash=444,
            file_reference=b"ref",
        ),
    ]
    assert result.documents is None
    assert result.users is None


async def test_an_html_message_serializes_its_media_as_files() -> None:
    message = types.InputRichMessage(
        html='<img src="tg://photo?id=pic">',
        skip_entity_detection=True,
        media=[
            types.InputRichMessageMedia(
                id="pic",
                media=types.InputMediaPhoto(_PHOTO_FILE_ID),
            ),
        ],
    )

    result = await message.write(client=None)

    assert result == raw.types.InputRichMessageHTML(
        rtl=None,
        noautolink=True,
        html='<img src="tg://photo?id=pic">',
        files=[
            raw.types.InputRichFilePhoto(
                id="pic",
                photo=raw.types.InputPhoto(
                    id=333,
                    access_hash=444,
                    file_reference=b"ref",
                ),
            ),
        ],
    )


async def test_a_markdown_message_serializes_a_document_media_as_a_document_file() -> None:
    message = types.InputRichMessage(
        markdown="[voice](tg://audio?id=note)",
        media=[
            types.InputRichMessageMedia(
                id="note",
                media=types.InputMediaVoiceNote(_VOICE_FILE_ID),
            ),
        ],
    )

    result = await message.write(client=None)

    assert result == raw.types.InputRichMessageMarkdown(
        rtl=None,
        noautolink=None,
        markdown="[voice](tg://audio?id=note)",
        files=[
            raw.types.InputRichFileDocument(
                id="note",
                document=raw.types.InputDocument(
                    id=111,
                    access_hash=222,
                    file_reference=b"ref",
                ),
            ),
        ],
    )


async def test_an_empty_message_is_rejected() -> None:
    message = types.InputRichMessage()

    with pytest.raises(ValueError, match="either blocks, markdown or html"):
        await message.write(client=None)
