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

import io
import os
from typing import TYPE_CHECKING, BinaryIO

import pyrogram
from pyrogram import raw, utils
from pyrogram.file_id import FileType

from .input_media import InputMedia

if TYPE_CHECKING:
    from collections.abc import Callable

    from ... import enums
    from ..messages_and_media import MessageEntity
    from pyrogram._typing import PathType


class InputMediaLivePhoto(InputMedia):
    """Represents a live photo to be sent.

    Parameters:
        media (``str`` | ``os.PathLike`` | ``BinaryIO``):
            Video of the live photo to send.
            Pass a file_id as string to send a video that exists on the Telegram servers or
            pass a file path as string to upload a new video that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get a video from the Internet.

        photo (``str`` | ``os.PathLike`` | ``BinaryIO``):
            The static photo to send.
            Pass a file_id as string to send a photo that exists on the Telegram servers or
            pass a file path as string to upload a new photo that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get a photo from the Internet.

        caption (``str``, *optional*):
            Caption of the video to be sent, 0-1024 characters.
            If not specified, the original caption is kept. Pass "" (empty string) to remove the caption.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        show_caption_above_media (``bool``, *optional*):
            Pass True, if the caption must be shown above the message media.

        has_spoiler (``bool``, *optional*):
            Pass True if the photo needs to be covered with a spoiler animation.

    Raises:
        FileNotFoundError: In case a local file path or ``os.PathLike`` doesn't point to an existing file.
        ValueError: In case a ``file_id`` is malformed or invalid.
    """

    def __init__(
        self,
        media: PathType | BinaryIO,
        photo: PathType | BinaryIO,
        thumb: PathType | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
        has_spoiler: bool | None = None,
    ):
        super().__init__(media, caption, parse_mode, caption_entities)

        self.photo = photo
        self.thumb = thumb
        self.show_caption_above_media = show_caption_above_media
        self.has_spoiler = has_spoiler

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        width: int = 0,
        height: int = 0,
        progress: Callable | None = None,
        progress_args: tuple = (),
        **kwargs,
    ) -> raw.base.InputMedia:
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await client.resolve_peer(chat_id)

        if isinstance(self.media, io.BytesIO) or os.path.isfile(self.media):
            uploaded_media = await client.invoke(
                raw.functions.messages.UploadMedia(
                    peer=peer,
                    media=raw.types.InputMediaUploadedDocument(
                        mime_type=client.guess_mime_type(self.media) or "video/mp4",
                        file=await client.save_file(
                            self.media, progress=progress, progress_args=progress_args
                        ),
                        spoiler=self.has_spoiler,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                duration=0,
                                w=width,
                                h=height,
                            ),
                        ],
                    ),
                ),
            )
            video = raw.types.InputDocument(
                id=uploaded_media.document.id,
                access_hash=uploaded_media.document.access_hash,
                file_reference=uploaded_media.document.file_reference,
            )
        elif isinstance(self.media, os.PathLike) or (
            isinstance(self.media, str) and ("/" in self.media or "\\" in self.media)
        ):
            raise FileNotFoundError(f"No such file or directory: {self.media}")
        else:
            video = utils.get_input_media_from_file_id(self.media, FileType.VIDEO).id

        if isinstance(self.photo, io.BytesIO) or os.path.isfile(self.photo):
            uploaded_photo = await client.invoke(
                raw.functions.messages.UploadMedia(
                    peer=peer,
                    media=raw.types.InputMediaUploadedPhoto(
                        file=await client.save_file(self.photo),
                        spoiler=self.has_spoiler,
                    ),
                ),
            )
            photo = raw.types.InputPhoto(
                id=uploaded_photo.photo.id,
                access_hash=uploaded_photo.photo.access_hash,
                file_reference=uploaded_photo.photo.file_reference,
            )
        elif isinstance(self.photo, os.PathLike) or (
            isinstance(self.photo, str) and ("/" in self.photo or "\\" in self.photo)
        ):
            raise FileNotFoundError(f"No such file or directory: {self.photo}")
        else:
            photo = utils.get_input_media_from_file_id(self.photo, FileType.PHOTO).id

        return raw.types.InputMediaPhoto(
            id=photo,
            live_photo=True,
            spoiler=self.has_spoiler,
            video=video,
        )
