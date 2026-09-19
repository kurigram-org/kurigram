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

from typing import TYPE_CHECKING, Final

import pyrogram
from pyrogram import raw, enums

if TYPE_CHECKING:
    from collections.abc import Callable

# Every `enums.ChatAction` member maps to exactly one raw constructor here, so
#  building the raw action never has to inspect the enum member's name at
#  runtime, and each lambda is checked against its own concrete raw type
#  instead of the `raw.base.SendMessageAction` union `action.value` carries.
_ACTIONS: Final[dict[enums.ChatAction, Callable[[], raw.base.SendMessageAction]]] = {
    enums.ChatAction.TYPING: raw.types.SendMessageTypingAction,
    enums.ChatAction.UPLOAD_PHOTO: lambda: raw.types.SendMessageUploadPhotoAction(progress=0),
    enums.ChatAction.RECORD_VIDEO: raw.types.SendMessageRecordVideoAction,
    enums.ChatAction.UPLOAD_VIDEO: lambda: raw.types.SendMessageUploadVideoAction(progress=0),
    enums.ChatAction.RECORD_AUDIO: raw.types.SendMessageRecordAudioAction,
    enums.ChatAction.UPLOAD_AUDIO: lambda: raw.types.SendMessageUploadAudioAction(progress=0),
    enums.ChatAction.UPLOAD_DOCUMENT: lambda: raw.types.SendMessageUploadDocumentAction(progress=0),
    enums.ChatAction.FIND_LOCATION: raw.types.SendMessageGeoLocationAction,
    enums.ChatAction.RECORD_VIDEO_NOTE: raw.types.SendMessageRecordRoundAction,
    enums.ChatAction.UPLOAD_VIDEO_NOTE: lambda: raw.types.SendMessageUploadRoundAction(progress=0),
    enums.ChatAction.PLAYING: raw.types.SendMessageGamePlayAction,
    enums.ChatAction.CHOOSE_CONTACT: raw.types.SendMessageChooseContactAction,
    enums.ChatAction.SPEAKING: raw.types.SpeakingInGroupCallAction,
    enums.ChatAction.IMPORT_HISTORY: lambda: raw.types.SendMessageHistoryImportAction(progress=0),
    enums.ChatAction.CHOOSE_STICKER: raw.types.SendMessageChooseStickerAction,
    enums.ChatAction.CANCEL: raw.types.SendMessageCancelAction,
}

# The two emoji-interaction actions are the only ones whose fields the caller decides, so
#  they are the only ones `_ACTIONS` cannot hold: `emoticon`, `message_id` and `interaction`
#  have no constant that would be right, the way `progress=0` is right above. This names the
#  parameters each of them needs, which is what the checks below report on.
_FIELD_ACTIONS: Final[dict[enums.ChatAction, frozenset[str]]] = {
    enums.ChatAction.EMOJI_INTERACTION: frozenset({"emoticon", "message_id", "interaction"}),
    enums.ChatAction.EMOJI_INTERACTION_SEEN: frozenset({"emoticon"}),
}


def _build_action(
    action: enums.ChatAction,
    *,
    emoticon: str | None,
    message_id: int | None,
    interaction: str | None,
) -> raw.base.SendMessageAction:
    accepted = _FIELD_ACTIONS.get(action, frozenset())
    given = {
        name
        for name, value in (
            ("emoticon", emoticon),
            ("message_id", message_id),
            ("interaction", interaction),
        )
        if value is not None
    }

    missing = sorted(accepted - given)
    if missing:
        raise ValueError(f"{action} needs {', '.join(missing)}")

    unexpected = sorted(given - accepted)
    if unexpected:
        raise ValueError(f"{action} takes no {', '.join(unexpected)}")

    if action is enums.ChatAction.EMOJI_INTERACTION:
        return raw.types.SendMessageEmojiInteraction(
            emoticon=emoticon,
            msg_id=message_id,
            interaction=raw.types.DataJSON(data=interaction),
        )

    if action is enums.ChatAction.EMOJI_INTERACTION_SEEN:
        return raw.types.SendMessageEmojiInteractionSeen(emoticon=emoticon)

    return _ACTIONS[action]()


class SendChatAction:
    async def send_chat_action(
        self: pyrogram.Client,
        chat_id: int | str,
        action: enums.ChatAction,
        business_connection_id: str | None = None,
        *,
        emoticon: str | None = None,
        message_id: int | None = None,
        interaction: str | None = None,
    ) -> bool:
        """Tell the other party that something is happening on your side.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            action (:obj:`~pyrogram.enums.ChatAction`):
                Type of action to broadcast.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            emoticon (``str``, *optional*):
                The animated emoji that was clicked.
                Required by :obj:`~pyrogram.enums.ChatAction.EMOJI_INTERACTION` and
                :obj:`~pyrogram.enums.ChatAction.EMOJI_INTERACTION_SEEN`, rejected by every other action.

            message_id (``int``, *optional*):
                Identifier of the message carrying the animated emoji that was clicked.
                Required by :obj:`~pyrogram.enums.ChatAction.EMOJI_INTERACTION`, rejected by every other action.

            interaction (``str``, *optional*):
                JSON-serialized description of the taps, as `the animated emoji documentation
                <https://core.telegram.org/api/animated-emojis>`_ specifies it: ``v`` is the object version,
                currently ``1``, and ``a`` is an array of taps, each with ``i``, the 1-based index of the
                animation played, and ``t``, the seconds since the previous tap.
                Required by :obj:`~pyrogram.enums.ChatAction.EMOJI_INTERACTION`, rejected by every other action.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            ValueError: In case the action was given fields it does not take, or was not given
                the fields it needs.

        Example:
            .. code-block:: python

                from pyrogram import enums

                # Send "typing" chat action
                await app.send_chat_action(chat_id, enums.ChatAction.TYPING)

                # Send "upload_video" chat action
                await app.send_chat_action(chat_id, enums.ChatAction.UPLOAD_VIDEO)

                # Send "playing" chat action
                await app.send_chat_action(chat_id, enums.ChatAction.PLAYING)

                # Cancel any current chat action
                await app.send_chat_action(chat_id, enums.ChatAction.CANCEL)

                # Report two taps on an animated emoji sent in message 1234
                await app.send_chat_action(
                    chat_id,
                    enums.ChatAction.EMOJI_INTERACTION,
                    emoticon="👍",
                    message_id=1234,
                    interaction='{"v": 1, "a": [{"i": 1, "t": 0.0}, {"i": 3, "t": 0.4}]}',
                )

                # Acknowledge the animation the other party sent back
                await app.send_chat_action(
                    chat_id,
                    enums.ChatAction.EMOJI_INTERACTION_SEEN,
                    emoticon="👍",
                )
        """

        return await self.invoke(
            raw.functions.messages.SetTyping(
                peer=await self.resolve_peer(chat_id),
                action=_build_action(
                    action,
                    emoticon=emoticon,
                    message_id=message_id,
                    interaction=interaction,
                ),
            ),
            business_connection_id=business_connection_id,
        )
