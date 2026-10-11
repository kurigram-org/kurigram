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

from enum import auto

from .auto_name import AutoName


class ChatEventActionType(AutoName):
    """Chat event action type enumeration used in :obj:`~pyrogram.types.ChatEvent`."""

    UNSUPPORTED = auto()
    "Unknown chat event action."

    MESSAGE_EDITED = auto()
    "A message was edited."

    MESSAGE_DELETED = auto()
    "A message was deleted."

    MESSAGE_PINNED = auto()
    "A message was pinned."

    MESSAGE_UNPINNED = auto()
    "A message was unpinned."

    POLL_STOPPED = auto()
    "A poll in a message was stopped."

    MEMBER_JOINED = auto()
    "A new member joined the chat."

    MEMBER_JOINED_BY_INVITE_LINK = auto()
    "A new member joined the chat via an invite link."

    MEMBER_JOINED_BY_REQUEST = auto()
    "A new member was accepted to the chat by an administrator."

    MEMBER_INVITED = auto()
    "A new chat member was invited."

    MEMBER_LEFT = auto()
    "A member left the chat."

    MEMBER_PROMOTED = auto()
    "A chat member has gained/lost administrator status, or the list of their administrator privileges has changed."

    MEMBER_RESTRICTED = auto()
    "A chat member was restricted/unrestricted or banned/unbanned, or the list of their restrictions has changed."

    MEMBER_TAG_CHANGED = auto()
    "A chat member tag has been changed."

    MEMBER_SUBSCRIPTION_EXTENDED = auto()
    "A chat member extended their subscription to the chat."

    AVAILABLE_REACTIONS_CHANGED = auto()
    "The chat available reactions were changed."

    BACKGROUND_CHANGED = auto()
    "The chat background was changed."

    DESCRIPTION_CHANGED = auto()
    "The chat description was changed."

    EMOJI_STATUS_CHANGED = auto()
    "The chat emoji status was changed."

    LINKED_CHAT_CHANGED = auto()
    "The linked chat of a supergroup was changed."

    LOCATION_CHANGED = auto()
    "The supergroup location was changed."

    MESSAGE_AUTO_DELETE_TIME_CHANGED = auto()
    "The message auto-delete timer was changed."

    PERMISSIONS_CHANGED = auto()
    "The chat permissions were changed."

    PHOTO_CHANGED = auto()
    "The chat photo was changed."

    SLOW_MODE_DELAY_CHANGED = auto()
    "The slow_mode_delay setting of a supergroup was changed."

    STICKER_SET_CHANGED = auto()
    "The supergroup sticker set was changed."

    EMOJI_STICKER_SET_CHANGED = auto()
    "The supergroup sticker set with allowed custom emoji was changed."

    TITLE_CHANGED = auto()
    "The chat title was changed."

    USERNAME_CHANGED = auto()
    "The chat editable username was changed."

    ACTIVE_USERNAMES_CHANGED = auto()
    "The chat active usernames were changed."

    ACCENT_COLOR_CHANGED = auto()
    "The chat accent color or background custom emoji were changed."

    PROFILE_ACCENT_COLOR_CHANGED = auto()
    "The chat's profile accent color or profile background custom emoji were changed."

    HAS_PROTECTED_CONTENT_TOGGLED = auto()
    "The has_protected_content setting of a chat was toggled."

    INVITES_TOGGLED = auto()
    "The can_invite_users permission of a supergroup chat was toggled."

    IS_ALL_HISTORY_AVAILABLE_TOGGLED = auto()
    "The is_all_history_available setting of a supergroup was toggled."

    HAS_AGGRESSIVE_ANTI_SPAM_ENABLED_TOGGLED = auto()
    "The has_aggressive_anti_spam_enabled setting of a supergroup was toggled."

    SIGN_MESSAGES_TOGGLED = auto()
    "The sign_messages setting of a channel was toggled."

    SHOW_MESSAGE_SENDER_TOGGLED = auto()
    "The show_message_sender setting of a channel was toggled."

    AUTOMATIC_TRANSLATION_TOGGLED = auto()
    "The has_automatic_translation setting of a channel was toggled."

    INVITE_LINK_EDITED = auto()
    "A chat invite link was edited."

    INVITE_LINK_REVOKED = auto()
    "A chat invite link was revoked."

    INVITE_LINK_DELETED = auto()
    "A chat invite link was deleted."

    VIDEO_CHAT_CREATED = auto()
    "A video chat was created."

    VIDEO_CHAT_ENDED = auto()
    "A video chat was ended."

    VIDEO_CHAT_MUTE_NEW_PARTICIPANTS_TOGGLED = auto()
    "The mute_new_participants setting of a video chat was toggled."

    VIDEO_CHAT_PARTICIPANT_IS_MUTED_TOGGLED = auto()
    "A video chat participant was muted or unmuted."

    VIDEO_CHAT_PARTICIPANT_VOLUME_LEVEL_CHANGED = auto()
    "A video chat participant volume level was changed."

    IS_FORUM_TOGGLED = auto()
    "The is_forum setting of a supergroup was toggled."

    FORUM_TOPIC_CREATED = auto()
    "A new forum topic was created."

    FORUM_TOPIC_EDITED = auto()
    "A forum topic was edited."

    FORUM_TOPIC_TOGGLE_IS_CLOSED = auto()
    "The General forum topic was closed or reopened."

    FORUM_TOPIC_TOGGLE_IS_HIDDEN = auto()
    "The General forum topic was hidden or unhidden."

    FORUM_TOPIC_DELETED = auto()
    "A forum topic was deleted."

    FORUM_TOPIC_PINNED = auto()
    "A pinned forum topic was changed."
