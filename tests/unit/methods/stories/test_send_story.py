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

import pytest

from pyrogram import raw

from .conftest import (
    STORY_FILE_NAME,
    UPLOADED_STORY_FILE,
    FakeClient,
    InvokeCalled,
    StoryMediaFactory,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "in_memory",
    [pytest.param(False, id="from-disk"), pytest.param(True, id="in-memory")],
)
async def test_supports_streaming_reaches_the_media_whichever_branch_built_it(
    story_client: FakeClient,
    story_media: StoryMediaFactory,
    *,
    in_memory: bool,
) -> None:
    # The disk branch omitted `supports_streaming` altogether, so a story uploaded from a
    #  path was posted non-streamable however the parameter was set.
    with pytest.raises(InvokeCalled) as exc_info:
        await story_client.send_story(
            chat_id=7,
            media=story_media(in_memory=in_memory),
            supports_streaming=True,
        )

    assert exc_info.value.query.media == raw.types.InputMediaUploadedDocument(
        mime_type="video/mp4",
        file=UPLOADED_STORY_FILE,
        attributes=[
            raw.types.DocumentAttributeVideo(
                supports_streaming=True,
                duration=0,
                w=0,
                h=0,
            ),
            raw.types.DocumentAttributeFilename(file_name=STORY_FILE_NAME),
        ],
    )
