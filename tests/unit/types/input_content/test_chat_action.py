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

from typing import Final, Protocol

import pytest

from pyrogram import raw, types

_INTERACTION: Final[str] = '{"v": 1, "a": [{"i": 1, "t": 0.0}]}'

_BARE_ACTIONS: Final = (
    pytest.param(
        types.ChatActionTyping,
        raw.types.SendMessageTypingAction,
        id="typing",
    ),
    pytest.param(
        types.ChatActionRecordVideo,
        raw.types.SendMessageRecordVideoAction,
        id="record-video",
    ),
    pytest.param(
        types.ChatActionRecordAudio,
        raw.types.SendMessageRecordAudioAction,
        id="record-audio",
    ),
    pytest.param(
        types.ChatActionFindLocation,
        raw.types.SendMessageGeoLocationAction,
        id="find-location",
    ),
    pytest.param(
        types.ChatActionRecordVideoNote,
        raw.types.SendMessageRecordRoundAction,
        id="record-video-note",
    ),
    pytest.param(
        types.ChatActionPlaying,
        raw.types.SendMessageGamePlayAction,
        id="playing",
    ),
    pytest.param(
        types.ChatActionChooseContact,
        raw.types.SendMessageChooseContactAction,
        id="choose-contact",
    ),
    pytest.param(
        types.ChatActionSpeaking,
        raw.types.SpeakingInGroupCallAction,
        id="speaking",
    ),
    pytest.param(
        types.ChatActionChooseSticker,
        raw.types.SendMessageChooseStickerAction,
        id="choose-sticker",
    ),
    pytest.param(
        types.ChatActionCancel,
        raw.types.SendMessageCancelAction,
        id="cancel",
    ),
)

_PROGRESS_ACTIONS: Final = (
    pytest.param(
        types.ChatActionUploadPhoto,
        raw.types.SendMessageUploadPhotoAction,
        id="upload-photo",
    ),
    pytest.param(
        types.ChatActionUploadVideo,
        raw.types.SendMessageUploadVideoAction,
        id="upload-video",
    ),
    pytest.param(
        types.ChatActionUploadAudio,
        raw.types.SendMessageUploadAudioAction,
        id="upload-audio",
    ),
    pytest.param(
        types.ChatActionUploadDocument,
        raw.types.SendMessageUploadDocumentAction,
        id="upload-document",
    ),
    pytest.param(
        types.ChatActionUploadVideoNote,
        raw.types.SendMessageUploadRoundAction,
        id="upload-video-note",
    ),
    pytest.param(
        types.ChatActionImportHistory,
        raw.types.SendMessageHistoryImportAction,
        id="import-history",
    ),
)


class _ProgressAction(Protocol):
    def __call__(self, progress: int = 0) -> types.ChatAction: ...


class _RawProgressAction(Protocol):
    def __call__(self, *, progress: int) -> raw.core.TLObject: ...


def test_the_base_action_refuses_to_write() -> None:
    with pytest.raises(NotImplementedError):
        types.ChatAction().write()


@pytest.mark.parametrize(("action", "expected_type"), _BARE_ACTIONS)
def test_a_bare_action_writes_its_raw_constructor(
    action: type[types.ChatAction],
    *,
    expected_type: type[raw.core.TLObject],
) -> None:
    result = action().write()

    # `TLObject.__eq__` walks `self.__slots__` only, so an action with no fields compares
    #  equal to anything: the type is asserted instead of the value.
    assert type(result) is expected_type


@pytest.mark.parametrize(("action", "expected_type"), _PROGRESS_ACTIONS)
def test_a_progress_action_carries_the_progress_the_caller_chose(
    action: _ProgressAction,
    *,
    expected_type: _RawProgressAction,
) -> None:
    result = action(progress=42).write()
    expected = expected_type(progress=42)

    assert type(result) is type(expected)
    assert result == expected


@pytest.mark.parametrize(("action", "expected_type"), _PROGRESS_ACTIONS)
def test_a_progress_action_defaults_to_zero(
    action: _ProgressAction,
    *,
    expected_type: _RawProgressAction,
) -> None:
    result = action().write()
    expected = expected_type(progress=0)

    assert type(result) is type(expected)
    assert result == expected


def test_emoji_interaction_writes_the_emoticon_the_message_and_the_payload() -> None:
    action = types.ChatActionEmojiInteraction(
        "👍",
        message_id=1234,
        interaction=_INTERACTION,
    )

    result = action.write()

    assert type(result) is raw.types.SendMessageEmojiInteraction
    assert result == raw.types.SendMessageEmojiInteraction(
        emoticon="👍",
        msg_id=1234,
        interaction=raw.types.DataJSON(data=_INTERACTION),
    )


def test_emoji_interaction_seen_writes_only_the_emoticon() -> None:
    result = types.ChatActionEmojiInteractionSeen("👍").write()

    assert type(result) is raw.types.SendMessageEmojiInteractionSeen
    assert result == raw.types.SendMessageEmojiInteractionSeen(emoticon="👍")


def test_every_subclass_has_a_row_in_this_module() -> None:
    covered: set[type[types.ChatAction]] = {
        parameters.values[0] for parameters in _BARE_ACTIONS + _PROGRESS_ACTIONS
    } | {
        types.ChatActionEmojiInteraction,
        types.ChatActionEmojiInteractionSeen,
    }

    assert covered == set(types.ChatAction.__subclasses__())
