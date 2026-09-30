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

from pyrogram import raw

from ..object import Object


class ChatAction(Object):
    """Content of a chat action to broadcast.

    It should be one of:

    - :obj:`~pyrogram.types.ChatActionTyping`
    - :obj:`~pyrogram.types.ChatActionUploadPhoto`
    - :obj:`~pyrogram.types.ChatActionRecordVideo`
    - :obj:`~pyrogram.types.ChatActionUploadVideo`
    - :obj:`~pyrogram.types.ChatActionRecordAudio`
    - :obj:`~pyrogram.types.ChatActionUploadAudio`
    - :obj:`~pyrogram.types.ChatActionUploadDocument`
    - :obj:`~pyrogram.types.ChatActionFindLocation`
    - :obj:`~pyrogram.types.ChatActionRecordVideoNote`
    - :obj:`~pyrogram.types.ChatActionUploadVideoNote`
    - :obj:`~pyrogram.types.ChatActionPlaying`
    - :obj:`~pyrogram.types.ChatActionChooseContact`
    - :obj:`~pyrogram.types.ChatActionSpeaking`
    - :obj:`~pyrogram.types.ChatActionImportHistory`
    - :obj:`~pyrogram.types.ChatActionChooseSticker`
    - :obj:`~pyrogram.types.ChatActionEmojiInteraction`
    - :obj:`~pyrogram.types.ChatActionEmojiInteractionSeen`
    - :obj:`~pyrogram.types.ChatActionCancel`
    """

    def write(self) -> raw.base.SendMessageAction:
        raise NotImplementedError


class ChatActionTyping(ChatAction):
    """Typing text message."""

    def write(self) -> raw.types.SendMessageTypingAction:
        return raw.types.SendMessageTypingAction()


class ChatActionUploadPhoto(ChatAction):
    """Uploading photo.

    Parameters:
        progress (``int``, *optional*):
            Upload progress, as a percentage.
    """

    def __init__(self, progress: int = 0) -> None:
        super().__init__()

        self.progress = progress

    def write(self) -> raw.types.SendMessageUploadPhotoAction:
        return raw.types.SendMessageUploadPhotoAction(progress=self.progress)


class ChatActionRecordVideo(ChatAction):
    """Recording video."""

    def write(self) -> raw.types.SendMessageRecordVideoAction:
        return raw.types.SendMessageRecordVideoAction()


class ChatActionUploadVideo(ChatAction):
    """Uploading video.

    Parameters:
        progress (``int``, *optional*):
            Upload progress, as a percentage.
    """

    def __init__(self, progress: int = 0) -> None:
        super().__init__()

        self.progress = progress

    def write(self) -> raw.types.SendMessageUploadVideoAction:
        return raw.types.SendMessageUploadVideoAction(progress=self.progress)


class ChatActionRecordAudio(ChatAction):
    """Recording audio."""

    def write(self) -> raw.types.SendMessageRecordAudioAction:
        return raw.types.SendMessageRecordAudioAction()


class ChatActionUploadAudio(ChatAction):
    """Uploading audio.

    Parameters:
        progress (``int``, *optional*):
            Upload progress, as a percentage.
    """

    def __init__(self, progress: int = 0) -> None:
        super().__init__()

        self.progress = progress

    def write(self) -> raw.types.SendMessageUploadAudioAction:
        return raw.types.SendMessageUploadAudioAction(progress=self.progress)


class ChatActionUploadDocument(ChatAction):
    """Uploading document.

    Parameters:
        progress (``int``, *optional*):
            Upload progress, as a percentage.
    """

    def __init__(self, progress: int = 0) -> None:
        super().__init__()

        self.progress = progress

    def write(self) -> raw.types.SendMessageUploadDocumentAction:
        return raw.types.SendMessageUploadDocumentAction(progress=self.progress)


class ChatActionFindLocation(ChatAction):
    """Finding location."""

    def write(self) -> raw.types.SendMessageGeoLocationAction:
        return raw.types.SendMessageGeoLocationAction()


class ChatActionRecordVideoNote(ChatAction):
    """Recording video note."""

    def write(self) -> raw.types.SendMessageRecordRoundAction:
        return raw.types.SendMessageRecordRoundAction()


class ChatActionUploadVideoNote(ChatAction):
    """Uploading video note.

    Parameters:
        progress (``int``, *optional*):
            Upload progress, as a percentage.
    """

    def __init__(self, progress: int = 0) -> None:
        super().__init__()

        self.progress = progress

    def write(self) -> raw.types.SendMessageUploadRoundAction:
        return raw.types.SendMessageUploadRoundAction(progress=self.progress)


class ChatActionPlaying(ChatAction):
    """Playing game."""

    def write(self) -> raw.types.SendMessageGamePlayAction:
        return raw.types.SendMessageGamePlayAction()


class ChatActionChooseContact(ChatAction):
    """Choosing contact."""

    def write(self) -> raw.types.SendMessageChooseContactAction:
        return raw.types.SendMessageChooseContactAction()


class ChatActionSpeaking(ChatAction):
    """Speaking in group call."""

    def write(self) -> raw.types.SpeakingInGroupCallAction:
        return raw.types.SpeakingInGroupCallAction()


class ChatActionImportHistory(ChatAction):
    """Importing history.

    Parameters:
        progress (``int``, *optional*):
            Import progress, as a percentage.
    """

    def __init__(self, progress: int = 0) -> None:
        super().__init__()

        self.progress = progress

    def write(self) -> raw.types.SendMessageHistoryImportAction:
        return raw.types.SendMessageHistoryImportAction(progress=self.progress)


class ChatActionChooseSticker(ChatAction):
    """Choosing sticker."""

    def write(self) -> raw.types.SendMessageChooseStickerAction:
        return raw.types.SendMessageChooseStickerAction()


class ChatActionEmojiInteraction(ChatAction):
    """Interacting with an animated emoji.

    Parameters:
        emoticon (``str``):
            The animated emoji that was clicked.

        message_id (``int``):
            Identifier of the message carrying the animated emoji that was clicked.

        interaction (``str``):
            JSON-serialized description of the taps, as `the animated emoji documentation
            <https://core.telegram.org/api/animated-emojis>`_ specifies it: ``v`` is the object
            version, currently ``1``, and ``a`` is an array of taps, each with ``i``, the 1-based
            index of the animation played, and ``t``, the seconds since the previous tap.
    """

    def __init__(
        self,
        emoticon: str,
        *,
        message_id: int,
        interaction: str,
    ) -> None:
        super().__init__()

        self.emoticon = emoticon
        self.message_id = message_id
        self.interaction = interaction

    def write(self) -> raw.types.SendMessageEmojiInteraction:
        return raw.types.SendMessageEmojiInteraction(
            emoticon=self.emoticon,
            msg_id=self.message_id,
            interaction=raw.types.DataJSON(data=self.interaction),
        )


class ChatActionEmojiInteractionSeen(ChatAction):
    """Watched an animated emoji interaction.

    Parameters:
        emoticon (``str``):
            The animated emoji the other party is interacting with.
    """

    def __init__(self, emoticon: str) -> None:
        super().__init__()

        self.emoticon = emoticon

    def write(self) -> raw.types.SendMessageEmojiInteractionSeen:
        return raw.types.SendMessageEmojiInteractionSeen(emoticon=self.emoticon)


class ChatActionCancel(ChatAction):
    """Cancel ongoing chat action."""

    def write(self) -> raw.types.SendMessageCancelAction:
        return raw.types.SendMessageCancelAction()
