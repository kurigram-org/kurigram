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


class ChatEventLogFilters(Object):
    """Represents a set of filters used to obtain a chat event log.

    Parameters:
        message_edits (``bool``):
            True, if message edits need to be returned.

        message_deletions (``bool``):
            True, if message deletions need to be returned.

        message_pins (``bool``):
            True, if pin/unpin events need to be returned.

        member_joins (``bool``):
            True, if members joining events need to be returned.

        member_leaves (``bool``):
            True, if members leaving events need to be returned.

        member_invites (``bool``):
            True, if invited member events need to be returned.

        member_promotions (``bool``):
            True, if member promotion/demotion events need to be returned.

        member_restrictions (``bool``):
            True, if member restricted/unrestricted/banned/unbanned events need to be returned.

        member_tag_changes (``bool``):
            True, if member tag and custom title change events need to be returned.

        info_changes (``bool``):
            True, if changes in chat information need to be returned.

        setting_changes (``bool``):
            True, if changes in chat settings need to be returned.

        invite_link_changes (``bool``):
            True, if changes to invite links need to be returned.

        video_chat_changes (``bool``):
            True, if video chat actions need to be returned.

        forum_changes (``bool``):
            True, if forum-related actions need to be returned.

        subscription_extensions (``bool``):
            True, if subscription extensions need to be returned.
    """

    def __init__(
        self,
        *,
        message_edits: bool | None = None,
        message_deletions: bool | None = None,
        message_pins: bool | None = None,
        member_joins: bool | None = None,
        member_leaves: bool | None = None,
        member_invites: bool | None = None,
        member_promotions: bool | None = None,
        member_restrictions: bool | None = None,
        member_tag_changes: bool | None = None,
        info_changes: bool | None = None,
        setting_changes: bool | None = None,
        invite_link_changes: bool | None = None,
        video_chat_changes: bool | None = None,
        forum_changes: bool | None = None,
        subscription_extensions: bool | None = None,
    ):
        super().__init__()

        self.message_edits = message_edits
        self.message_deletions = message_deletions
        self.message_pins = message_pins
        self.member_joins = member_joins
        self.member_leaves = member_leaves
        self.member_invites = member_invites
        self.member_promotions = member_promotions
        self.member_restrictions = member_restrictions
        self.member_tag_changes = member_tag_changes
        self.info_changes = info_changes
        self.setting_changes = setting_changes
        self.invite_link_changes = invite_link_changes
        self.video_chat_changes = video_chat_changes
        self.forum_changes = forum_changes
        self.subscription_extensions = subscription_extensions

    def write(self) -> raw.types.ChannelAdminLogEventsFilter:
        join = None
        leave = None
        invite = None
        ban = None
        unban = None
        kick = None
        unkick = None
        promote = None
        demote = None
        info = None
        settings = None
        pinned = None
        edit = None
        delete = None
        group_call = None
        invites = None
        forums = None
        sub_extend = None
        edit_rank = None

        if self.member_restrictions:
            ban = True
            unban = True
            kick = True
            unkick = True

        if self.member_promotions:
            promote = True
            demote = True

        if self.member_joins:
            join = True
            invite = True

        if self.info_changes:
            info = True

        if self.setting_changes:
            settings = True

        if self.invite_link_changes:
            invites = True

        if self.message_deletions:
            delete = True

        if self.message_edits:
            edit = True

        if self.message_pins:
            pinned = True

        if self.member_leaves:
            leave = True

        if self.video_chat_changes:
            group_call = True

        if self.forum_changes:
            forums = True

        if self.subscription_extensions:
            sub_extend = True

        if self.member_tag_changes:
            edit_rank = True

        return raw.types.ChannelAdminLogEventsFilter(
            join=join,
            leave=leave,
            invite=invite,
            ban=ban,
            unban=unban,
            kick=kick,
            unkick=unkick,
            promote=promote,
            demote=demote,
            info=info,
            settings=settings,
            pinned=pinned,
            edit=edit,
            delete=delete,
            group_call=group_call,
            invites=invites,
            forums=forums,
            sub_extend=sub_extend,
            edit_rank=edit_rank,
        )
