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

from typing import TYPE_CHECKING

from ..object import Object

if TYPE_CHECKING:
    from pyrogram import types


class ChatEventAction(Object):
    """Contains information about chat event.

    It can be one of:

    - :obj:`~pyrogram.types.ChatEventActionMessageEdited`
    - :obj:`~pyrogram.types.ChatEventActionMessageDeleted`
    - :obj:`~pyrogram.types.ChatEventActionMessagePinned`
    - :obj:`~pyrogram.types.ChatEventActionMessageUnpinned`
    - :obj:`~pyrogram.types.ChatEventActionPollStopped`
    - :obj:`~pyrogram.types.ChatEventActionMemberJoined`
    - :obj:`~pyrogram.types.ChatEventActionMemberJoinedByInviteLink`
    - :obj:`~pyrogram.types.ChatEventActionMemberJoinedByRequest`
    - :obj:`~pyrogram.types.ChatEventActionMemberInvited`
    - :obj:`~pyrogram.types.ChatEventActionMemberLeft`
    - :obj:`~pyrogram.types.ChatEventActionMemberPromoted`
    - :obj:`~pyrogram.types.ChatEventActionMemberRestricted`
    - :obj:`~pyrogram.types.ChatEventActionMemberTagChanged`
    - :obj:`~pyrogram.types.ChatEventActionMemberSubscriptionExtended`
    - :obj:`~pyrogram.types.ChatEventActionAvailableReactionsChanged`
    - :obj:`~pyrogram.types.ChatEventActionBackgroundChanged`
    - :obj:`~pyrogram.types.ChatEventActionDescriptionChanged`
    - :obj:`~pyrogram.types.ChatEventActionEmojiStatusChanged`
    - :obj:`~pyrogram.types.ChatEventActionLinkedChatChanged`
    - :obj:`~pyrogram.types.ChatEventActionLocationChanged`
    - :obj:`~pyrogram.types.ChatEventActionMessageAutoDeleteTimeChanged`
    - :obj:`~pyrogram.types.ChatEventActionPermissionsChanged`
    - :obj:`~pyrogram.types.ChatEventActionPhotoChanged`
    - :obj:`~pyrogram.types.ChatEventActionSlowModeDelayChanged`
    - :obj:`~pyrogram.types.ChatEventActionStickerSetChanged`
    - :obj:`~pyrogram.types.ChatEventActionCustomEmojiStickerSetChanged`
    - :obj:`~pyrogram.types.ChatEventActionTitleChanged`
    - :obj:`~pyrogram.types.ChatEventActionUsernameChanged`
    - :obj:`~pyrogram.types.ChatEventActionActiveUsernamesChanged`
    - :obj:`~pyrogram.types.ChatEventActionAccentColorChanged`
    - :obj:`~pyrogram.types.ChatEventActionProfileAccentColorChanged`
    - :obj:`~pyrogram.types.ChatEventActionHasProtectedContentToggled`
    - :obj:`~pyrogram.types.ChatEventActionInvitesToggled`
    - :obj:`~pyrogram.types.ChatEventActionIsAllHistoryAvailableToggled`
    - :obj:`~pyrogram.types.ChatEventActionHasAggressiveAntiSpamEnabledToggled`
    - :obj:`~pyrogram.types.ChatEventActionSignMessagesToggled`
    - :obj:`~pyrogram.types.ChatEventActionShowMessageSenderToggled`
    - :obj:`~pyrogram.types.ChatEventActionAutomaticTranslationToggled`
    - :obj:`~pyrogram.types.ChatEventActionInviteLinkEdited`
    - :obj:`~pyrogram.types.ChatEventActionInviteLinkRevoked`
    - :obj:`~pyrogram.types.ChatEventActionInviteLinkDeleted`
    - :obj:`~pyrogram.types.ChatEventActionVideoChatCreated`
    - :obj:`~pyrogram.types.ChatEventActionVideoChatEnded`
    - :obj:`~pyrogram.types.ChatEventActionVideoChatMuteNewParticipantsToggled`
    - :obj:`~pyrogram.types.ChatEventActionVideoChatParticipantIsMutedToggled`
    - :obj:`~pyrogram.types.ChatEventActionVideoChatParticipantVolumeLevelChanged`
    - :obj:`~pyrogram.types.ChatEventActionIsForumToggled`
    - :obj:`~pyrogram.types.ChatEventActionForumTopicCreated`
    - :obj:`~pyrogram.types.ChatEventActionForumTopicEdited`
    - :obj:`~pyrogram.types.ChatEventActionForumTopicToggleIsClosed`
    - :obj:`~pyrogram.types.ChatEventActionForumTopicToggleIsHidden`
    - :obj:`~pyrogram.types.ChatEventActionForumTopicDeleted`
    - :obj:`~pyrogram.types.ChatEventActionForumTopicPinned`
    """


class ChatEventActionMessageEdited(ChatEventAction):
    """A message was edited.

    Parameters:
        old_message (:obj:`~pyrogram.types.Message`):
            The original message before the edit.

        new_message (:obj:`~pyrogram.types.Message`):
            The message after it was edited.
    """

    def __init__(self, *, old_message: types.Message, new_message: types.Message):
        super().__init__()

        self.old_message = old_message
        self.new_message = new_message


class ChatEventActionMessageDeleted(ChatEventAction):
    """A message was deleted.

    Parameters:
        message (:obj:`~pyrogram.types.Message`):
            Deleted message.

        can_report_anti_spam_false_positive (``bool``):
            True, if the message deletion can be reported.
    """

    def __init__(self, *, message: types.Message, can_report_anti_spam_false_positive: bool):
        super().__init__()

        self.message = message
        self.can_report_anti_spam_false_positive = can_report_anti_spam_false_positive


class ChatEventActionMessagePinned(ChatEventAction):
    """A message was pinned.

    Parameters:
        message (:obj:`~pyrogram.types.Message`):
            Pinned message.
    """

    def __init__(self, *, message: types.Message):
        super().__init__()

        self.message = message


class ChatEventActionMessageUnpinned(ChatEventAction):
    """A message was unpinned.

    Parameters:
        message (:obj:`~pyrogram.types.Message`):
            Unpinned message.
    """

    def __init__(self, *, message: types.Message):
        super().__init__()

        self.message = message


class ChatEventActionPollStopped(ChatEventAction):
    """A poll in a message was stopped.

    Parameters:
        message (:obj:`~pyrogram.types.Message`):
            The message with the poll.
    """

    def __init__(self, *, message: types.Message):
        super().__init__()

        self.message = message


class ChatEventActionMemberJoined(ChatEventAction):
    """A new member joined the chat.

    Currently holds no information.
    """

    def __init__(self):
        super().__init__()


class ChatEventActionMemberJoinedByInviteLink(ChatEventAction):
    """A new member joined the chat via an invite link.

    Parameters:
        invite_link (:obj:`~pyrogram.types.ChatInviteLink`):
            Invite link used to join the chat.

        via_chat_folder_invite_link (``bool``):
            True, if the user has joined the chat using an invite link for a chat folder.
    """

    def __init__(self, *, invite_link: types.ChatInviteLink, via_chat_folder_invite_link: bool):
        super().__init__()

        self.invite_link = invite_link
        self.via_chat_folder_invite_link = via_chat_folder_invite_link


class ChatEventActionMemberJoinedByRequest(ChatEventAction):
    """A new member was accepted to the chat by an administrator.

    Parameters:
        approver_user (:obj:`~pyrogram.types.User`):
            The chat administrator that approved user join request.

        invite_link (:obj:`~pyrogram.types.ChatInviteLink`, *optional*):
            Invite link used to join the chat.
    """

    def __init__(
        self, *, approver_user: types.User, invite_link: types.ChatInviteLink | None = None
    ):
        super().__init__()

        self.approver_user = approver_user
        self.invite_link = invite_link


class ChatEventActionMemberInvited(ChatEventAction):
    """A new chat member was invited.

    Parameters:
        member (:obj:`~pyrogram.types.ChatMember`):
            New member.
    """

    def __init__(self, *, member: types.ChatMember):
        super().__init__()

        self.member = member


class ChatEventActionMemberLeft(ChatEventAction):
    """A member left the chat.

    Currently holds no information.
    """

    def __init__(self):
        super().__init__()


class ChatEventActionMemberPromoted(ChatEventAction):
    """A chat member has gained/lost administrator status, or the list of their administrator privileges has changed.

    Parameters:
        old_member (:obj:`~pyrogram.types.ChatMember`):
            Previous status of the chat member.

        new_member (:obj:`~pyrogram.types.ChatMember`):
            New status of the chat member.
    """

    def __init__(self, *, old_member: types.ChatMember, new_member: types.ChatMember):
        super().__init__()

        self.old_member = old_member
        self.new_member = new_member


class ChatEventActionMemberRestricted(ChatEventAction):
    """A chat member was restricted/unrestricted or banned/unbanned, or the list of their restrictions has changed.

    Parameters:
        old_member (:obj:`~pyrogram.types.ChatMember`):
            Previous status of the chat member.

        new_member (:obj:`~pyrogram.types.ChatMember`):
            New status of the chat member.
    """

    def __init__(self, *, old_member: types.ChatMember, new_member: types.ChatMember):
        super().__init__()

        self.old_member = old_member
        self.new_member = new_member


class ChatEventActionMemberTagChanged(ChatEventAction):
    """A chat member tag has been changed.

    Parameters:
        user (:obj:`~pyrogram.types.User`):
            Affected chat member.

        old_tag (``str``):
            Previous tag of the chat member.

        new_tag (``str``):
            New tag of the chat member.
    """

    def __init__(self, *, user: types.User, old_tag: str, new_tag: str):
        super().__init__()

        self.user = user
        self.old_tag = old_tag
        self.new_tag = new_tag


class ChatEventActionMemberSubscriptionExtended(ChatEventAction):
    """A chat member extended their subscription to the chat.

    Parameters:
        old_member (:obj:`~pyrogram.types.ChatMember`):
            Previous status of the chat member.

        new_member (:obj:`~pyrogram.types.ChatMember`):
            New status of the chat member.
    """

    def __init__(self, *, old_member: types.ChatMember, new_member: types.ChatMember):
        super().__init__()

        self.old_member = old_member
        self.new_member = new_member


class ChatEventActionAvailableReactionsChanged(ChatEventAction):
    """The chat available reactions were changed.

    Parameters:
        old_available_reactions (:obj:`~pyrogram.types.ChatReactions`):
            Previous chat available reactions.

        new_available_reactions (:obj:`~pyrogram.types.ChatReactions`):
            New chat available reactions.
    """

    def __init__(
        self,
        *,
        old_available_reactions: types.ChatReactions,
        new_available_reactions: types.ChatReactions,
    ):
        super().__init__()

        self.old_available_reactions = old_available_reactions
        self.new_available_reactions = new_available_reactions


class ChatEventActionBackgroundChanged(ChatEventAction):
    """The chat background was changed.

    Parameters:
        old_background (:obj:`~pyrogram.types.ChatBackground`, *optional*):
            Previous background.

        new_background (:obj:`~pyrogram.types.ChatBackground`, *optional*):
            New background.
    """

    def __init__(
        self,
        *,
        old_background: types.ChatBackground | None = None,
        new_background: types.ChatBackground | None = None,
    ):
        super().__init__()

        self.old_background = old_background
        self.new_background = new_background


class ChatEventActionDescriptionChanged(ChatEventAction):
    """The chat description was changed.

    Parameters:
        old_description (``str``):
            Previous chat description.

        new_description (``str``):
            New chat description.
    """

    def __init__(self, *, old_description: str, new_description: str):
        super().__init__()

        self.old_description = old_description
        self.new_description = new_description


class ChatEventActionEmojiStatusChanged(ChatEventAction):
    """The chat emoji status was changed.

    Parameters:
        old_emoji_status (:obj:`~pyrogram.types.EmojiStatus`, *optional*):
            Previous chat description.

        new_emoji_status (:obj:`~pyrogram.types.EmojiStatus`, *optional*):
            New chat description.
    """

    def __init__(
        self,
        *,
        old_emoji_status: types.EmojiStatus | None = None,
        new_emoji_status: types.EmojiStatus | None = None,
    ):
        super().__init__()

        self.old_emoji_status = old_emoji_status
        self.new_emoji_status = new_emoji_status


class ChatEventActionLinkedChatChanged(ChatEventAction):
    """The linked chat of a supergroup was changed.

    Parameters:
        old_linked_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Previous supergroup linked chat.

        new_linked_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            New supergroup linked chat.
    """

    def __init__(
        self,
        *,
        old_linked_chat: types.Chat | None = None,
        new_linked_chat: types.Chat | None = None,
    ):
        super().__init__()

        self.old_linked_chat = old_linked_chat
        self.new_linked_chat = new_linked_chat


class ChatEventActionLocationChanged(ChatEventAction):
    """The supergroup location was changed.

    Parameters:
        old_location (:obj:`~pyrogram.types.Location`, *optional*):
            Previous location.

        new_location (:obj:`~pyrogram.types.Location`, *optional*):
            New location.
    """

    def __init__(
        self,
        *,
        old_location: types.Location | None = None,
        new_location: types.Location | None = None,
    ):
        super().__init__()

        self.old_location = old_location
        self.new_location = new_location


class ChatEventActionMessageAutoDeleteTimeChanged(ChatEventAction):
    """The message auto-delete timer was changed.

    Parameters:
        old_message_auto_delete_time (``int``):
            Previous value of message_auto_delete_time.

        new_message_auto_delete_time (``int``):
            New value of message_auto_delete_time.
    """

    def __init__(self, *, old_message_auto_delete_time: int, new_message_auto_delete_time: int):
        super().__init__()

        self.old_message_auto_delete_time = old_message_auto_delete_time
        self.new_message_auto_delete_time = new_message_auto_delete_time


class ChatEventActionPermissionsChanged(ChatEventAction):
    """The chat permissions were changed.

    Parameters:
        old_permissions (:obj:`~pyrogram.types.ChatPermissions`):
            Previous chat permissions.

        new_permissions (:obj:`~pyrogram.types.ChatPermissions`):
            New chat permissions.
    """

    def __init__(
        self, *, old_permissions: types.ChatPermissions, new_permissions: types.ChatPermissions
    ):
        super().__init__()

        self.old_permissions = old_permissions
        self.new_permissions = new_permissions


class ChatEventActionPhotoChanged(ChatEventAction):
    """The chat photo was changed.

    Parameters:
        old_photo (:obj:`~pyrogram.types.ChatPhoto`, *optional*):
            Previous chat photo value.

        new_photo (:obj:`~pyrogram.types.ChatPhoto`, *optional*):
            New chat photo value.
    """

    def __init__(
        self, *, old_photo: types.ChatPhoto | None = None, new_photo: types.ChatPhoto | None = None
    ):
        super().__init__()

        self.old_photo = old_photo
        self.new_photo = new_photo


class ChatEventActionSlowModeDelayChanged(ChatEventAction):
    """The slow_mode_delay setting of a supergroup was changed.

    Parameters:
        old_slow_mode_delay (``int``):
            Previous value of slow_mode_delay, in seconds.

        new_slow_mode_delay (``int``):
            New value of slow_mode_delay, in seconds.
    """

    def __init__(self, *, old_slow_mode_delay: int, new_slow_mode_delay: int):
        super().__init__()

        self.old_slow_mode_delay = old_slow_mode_delay
        self.new_slow_mode_delay = new_slow_mode_delay


class ChatEventActionStickerSetChanged(ChatEventAction):
    """The supergroup sticker set was changed.

    Parameters:
        old_sticker_set_id (``int``, *optional*):
            Previous identifier of the chat sticker set.

        new_sticker_set_id (``int``, *optional*):
            New identifier of the chat sticker set.
    """

    def __init__(
        self, *, old_sticker_set_id: int | None = None, new_sticker_set_id: int | None = None
    ):
        super().__init__()

        self.old_sticker_set_id = old_sticker_set_id
        self.new_sticker_set_id = new_sticker_set_id


class ChatEventActionCustomEmojiStickerSetChanged(ChatEventAction):
    """The supergroup sticker set with allowed custom emoji was changed.

    Parameters:
        old_sticker_set_id (``int``, *optional*):
            Previous identifier of the chat sticker set.

        new_sticker_set_id (``int``, *optional*):
            New identifier of the chat sticker set.
    """

    def __init__(
        self, *, old_sticker_set_id: int | None = None, new_sticker_set_id: int | None = None
    ):
        super().__init__()

        self.old_sticker_set_id = old_sticker_set_id
        self.new_sticker_set_id = new_sticker_set_id


class ChatEventActionTitleChanged(ChatEventAction):
    """The chat title was changed.

    Parameters:
        old_title (``str``):
            Previous chat title.

        new_title (``str``):
            New chat title.
    """

    def __init__(self, *, old_title: str, new_title: str):
        super().__init__()

        self.old_title = old_title
        self.new_title = new_title


class ChatEventActionUsernameChanged(ChatEventAction):
    """The chat editable username was changed.

    Parameters:
        old_username (``str``):
            Previous chat username.

        new_username (``str``):
            New chat username.
    """

    def __init__(self, *, old_username: str, new_username: str):
        super().__init__()

        self.old_username = old_username
        self.new_username = new_username


class ChatEventActionActiveUsernamesChanged(ChatEventAction):
    """The chat active usernames were changed.

    Parameters:
        old_usernames (List of ``str``):
            Previous list of active usernames.

        new_usernames (List of ``str``):
            New list of active usernames.
    """

    def __init__(self, *, old_usernames: list[str], new_usernames: list[str]):
        super().__init__()

        self.old_usernames = old_usernames
        self.new_usernames = new_usernames


class ChatEventActionAccentColorChanged(ChatEventAction):
    """The chat accent color or background custom emoji were changed.

    Parameters:
        old_accent_color_id (``int``):
            Previous identifier of chat accent color.

        old_background_custom_emoji_id (``str``, *optional*):
            Previous identifier of the custom emoji.

        new_accent_color_id (``int``):
            New identifier of chat accent color.

        new_background_custom_emoji_id (``str``, *optional*):
            New identifier of the custom emoji.
    """

    def __init__(
        self,
        *,
        old_accent_color_id: int,
        old_background_custom_emoji_id: str | None = None,
        new_accent_color_id: int,
        new_background_custom_emoji_id: str | None = None,
    ):
        super().__init__()

        self.old_accent_color_id = old_accent_color_id
        self.old_background_custom_emoji_id = old_background_custom_emoji_id
        self.new_accent_color_id = new_accent_color_id
        self.new_background_custom_emoji_id = new_background_custom_emoji_id


class ChatEventActionProfileAccentColorChanged(ChatEventAction):
    """The chat's profile accent color or profile background custom emoji were changed.

    Parameters:
        old_profile_accent_color_id (``int``, *optional*):
            Previous identifier of chat's profile accent color.

        old_profile_background_custom_emoji_id (``str``, *optional*):
            Previous identifier of the custom emoji.

        new_profile_accent_color_id (``int``, *optional*):
            New identifier of chat's profile accent color.

        new_profile_background_custom_emoji_id (``str``, *optional*):
            New identifier of the custom emojie.
    """

    def __init__(
        self,
        *,
        old_profile_accent_color_id: int | None = None,
        old_profile_background_custom_emoji_id: str | None = None,
        new_profile_accent_color_id: int | None = None,
        new_profile_background_custom_emoji_id: str | None = None,
    ):
        super().__init__()

        self.old_profile_accent_color_id = old_profile_accent_color_id
        self.old_profile_background_custom_emoji_id = old_profile_background_custom_emoji_id
        self.new_profile_accent_color_id = new_profile_accent_color_id
        self.new_profile_background_custom_emoji_id = new_profile_background_custom_emoji_id


class ChatEventActionHasProtectedContentToggled(ChatEventAction):
    """The has_protected_content setting of a chat was toggled.

    Parameters:
        has_protected_content (``bool``):
            New value of has_protected_content.
    """

    def __init__(self, has_protected_content: bool):
        super().__init__()

        self.has_protected_content = has_protected_content


class ChatEventActionInvitesToggled(ChatEventAction):
    """The can_invite_users permission of a supergroup chat was toggled.

    Parameters:
        can_invite_users (``bool``):
            New value of can_invite_users permission.
    """

    def __init__(self, can_invite_users: bool):
        super().__init__()

        self.can_invite_users = can_invite_users


class ChatEventActionIsAllHistoryAvailableToggled(ChatEventAction):
    """The is_all_history_available setting of a supergroup was toggled.

    Parameters:
        is_all_history_available (``bool``):
            New value of is_all_history_available.
    """

    def __init__(self, is_all_history_available: bool):
        super().__init__()

        self.is_all_history_available = is_all_history_available


class ChatEventActionHasAggressiveAntiSpamEnabledToggled(ChatEventAction):
    """The has_aggressive_anti_spam_enabled setting of a supergroup was toggled.

    Parameters:
        has_aggressive_anti_spam_enabled (``bool``):
            New value of has_aggressive_anti_spam_enabled.
    """

    def __init__(self, has_aggressive_anti_spam_enabled: bool):
        super().__init__()

        self.has_aggressive_anti_spam_enabled = has_aggressive_anti_spam_enabled


class ChatEventActionSignMessagesToggled(ChatEventAction):
    """The sign_messages setting of a channel was toggled.

    Parameters:
        sign_messages (``bool``):
            New value of sign_messages.
    """

    def __init__(self, sign_messages: bool):
        super().__init__()

        self.sign_messages = sign_messages


class ChatEventActionShowMessageSenderToggled(ChatEventAction):
    """The show_message_sender setting of a channel was toggled.

    Parameters:
        show_message_sender (``bool``):
            New value of show_message_sender.
    """

    def __init__(self, show_message_sender: bool):
        super().__init__()

        self.show_message_sender = show_message_sender


class ChatEventActionAutomaticTranslationToggled(ChatEventAction):
    """The has_automatic_translation setting of a channel was toggled.

    Parameters:
        has_automatic_translation (``bool``):
            New value of has_automatic_translation.
    """

    def __init__(self, has_automatic_translation: bool):
        super().__init__()

        self.has_automatic_translation = has_automatic_translation


class ChatEventActionInviteLinkEdited(ChatEventAction):
    """A chat invite link was edited.

    Parameters:
        old_invite_link (:obj:`~pyrogram.types.ChatInviteLink`):
            Previous information about the invite link.

        new_invite_link (:obj:`~pyrogram.types.ChatInviteLink`):
            New information about the invite link.
    """

    def __init__(
        self, old_invite_link: types.ChatInviteLink, new_invite_link: types.ChatInviteLink
    ):
        super().__init__()

        self.old_invite_link = old_invite_link
        self.new_invite_link = new_invite_link


class ChatEventActionInviteLinkRevoked(ChatEventAction):
    """A chat invite link was revoked.

    Parameters:
        invite_link (:obj:`~pyrogram.types.ChatInviteLink`):
            The invite link.
    """

    def __init__(self, invite_link: types.ChatInviteLink):
        super().__init__()

        self.invite_link = invite_link


class ChatEventActionInviteLinkDeleted(ChatEventAction):
    """A revoked chat invite link was deleted.

    Parameters:
        invite_link (:obj:`~pyrogram.types.ChatInviteLink`):
            The invite link.
    """

    def __init__(self, invite_link: types.ChatInviteLink):
        super().__init__()

        self.invite_link = invite_link


class ChatEventActionVideoChatCreated(ChatEventAction):
    """A video chat was created.

    Parameters:
        group_call_id (``int``):
            Identifier of the video chat.
    """

    def __init__(self, group_call_id: int):
        super().__init__()

        self.group_call_id = group_call_id


class ChatEventActionVideoChatEnded(ChatEventAction):
    """A video chat was ended.

    Parameters:
        group_call_id (``int``):
            Identifier of the video chat.
    """

    def __init__(self, group_call_id: int):
        super().__init__()

        self.group_call_id = group_call_id


class ChatEventActionVideoChatMuteNewParticipantsToggled(ChatEventAction):
    """The mute_new_participants setting of a video chat was toggled.

    Parameters:
        mute_new_participants (``bool``):
            New value of the mute_new_participants setting.
    """

    def __init__(self, mute_new_participants: bool):
        super().__init__()

        self.mute_new_participants = mute_new_participants


class ChatEventActionVideoChatParticipantIsMutedToggled(ChatEventAction):
    """A video chat participant was muted or unmuted.

    Parameters:
        participant (:obj:`~pyrogram.types.Chat`):
            Identifier of the affected group call participant.

        is_muted (``bool``):
            New value of is_muted.
    """

    def __init__(self, participant: types.Chat, is_muted: bool):
        super().__init__()

        self.participant = participant
        self.is_muted = is_muted


class ChatEventActionVideoChatParticipantVolumeLevelChanged(ChatEventAction):
    """A video chat participant volume level was changed.

    Parameters:
        participant (:obj:`~pyrogram.types.Chat`):
            Identifier of the affected group call participant.

        volume_level (``int``):
            New value of volume_level, 1-20000 in hundreds of percents.
    """

    def __init__(self, participant: types.Chat, volume_level: int):
        super().__init__()

        self.participant = participant
        self.volume_level = volume_level


class ChatEventActionIsForumToggled(ChatEventAction):
    """The is_forum setting of a supergroup was toggled.

    Parameters:
        is_forum (``bool``):
            New value of is_forum.
    """

    def __init__(self, is_forum: bool):
        super().__init__()

        self.is_forum = is_forum


class ChatEventActionForumTopicCreated(ChatEventAction):
    """A forum topic was created.

    Parameters:
        topic_info (:obj:`~pyrogram.types.ForumTopic`):
            Information about the topic.
    """

    def __init__(self, topic_info: types.ForumTopic):
        super().__init__()

        self.topic_info = topic_info


class ChatEventActionForumTopicEdited(ChatEventAction):
    """A forum topic was edited.

    Parameters:
        old_topic_info (:obj:`~pyrogram.types.ForumTopic`):
            Old information about the topic.

        new_topic_info (:obj:`~pyrogram.types.ForumTopic`):
            New information about the topic.
    """

    def __init__(self, old_topic_info: types.ForumTopic, new_topic_info: types.ForumTopic):
        super().__init__()

        self.old_topic_info = old_topic_info
        self.new_topic_info = new_topic_info


class ChatEventActionForumTopicToggleIsClosed(ChatEventAction):
    """A forum topic was closed or reopened.

    Parameters:
        topic_info (:obj:`~pyrogram.types.ForumTopic`):
            New information about the topic.
    """

    def __init__(self, topic_info: types.ForumTopic):
        super().__init__()

        self.topic_info = topic_info


class ChatEventActionForumTopicToggleIsHidden(ChatEventAction):
    """The General forum topic was hidden or unhidden.

    Parameters:
        topic_info (:obj:`~pyrogram.types.ForumTopic`):
            New information about the topic.
    """

    def __init__(self, topic_info: types.ForumTopic):
        super().__init__()

        self.topic_info = topic_info


class ChatEventActionForumTopicDeleted(ChatEventAction):
    """A forum topic was deleted.

    Parameters:
        topic_info (:obj:`~pyrogram.types.ForumTopic`):
            Information about the topic.
    """

    def __init__(self, topic_info: types.ForumTopic):
        super().__init__()

        self.topic_info = topic_info


class ChatEventActionForumTopicPinned(ChatEventAction):
    """A pinned forum topic was changed.

    Parameters:
        old_topic_info (:obj:`~pyrogram.types.ForumTopic`, *optional*):
            Information about the old pinned topic.

        new_topic_info (:obj:`~pyrogram.types.ForumTopic`, *optional*):
            New information about the new pinned topic.
    """

    def __init__(
        self,
        old_topic_info: types.ForumTopic | None = None,
        new_topic_info: types.ForumTopic | None = None,
    ):
        super().__init__()

        self.old_topic_info = old_topic_info
        self.new_topic_info = new_topic_info
