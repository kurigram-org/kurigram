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
from datetime import datetime

import pyrogram
from pyrogram import enums, raw, types, utils

from ..object import Object

if TYPE_CHECKING:
    from datetime import datetime


class ChatEvent(Object):
    """A chat event from the recent actions log (also known as admin log).

    See ``action`` to know which kind of event this is and the relative attributes to get the event content.

    Parameters:
        id (``int``):
            Chat event identifier.

        date (:py:obj:`~datetime.datetime`):
            Date of the event.

        member (:obj:`~pyrogram.types.Chat`):
            User or chat who performed the action.

        action (:obj:`~pyrogram.enums.ChatEventActionType`):
            Event action.
            This field will contain the enumeration type of the chat event action.
            You can use ``action = getattr(event, event.action.value)`` to access the chat event.

        message_edited (:obj:`~pyrogram.types.ChatEventActionMessageEdited`, *optional*):
            A message was edited.

        message_deleted (:obj:`~pyrogram.types.ChatEventActionMessageDeleted`, *optional*):
            A message was deleted.

        message_pinned (:obj:`~pyrogram.types.ChatEventActionMessagePinned`, *optional*):
            A message was pinned.

        message_unpinned (:obj:`~pyrogram.types.ChatEventActionMessageUnpinned`, *optional*):
            A message was unpinned.

        poll_stopped (:obj:`~pyrogram.types.ChatEventActionPollStopped`, *optional*):
            A poll in a message was stopped.

        member_joined (:obj:`~pyrogram.types.ChatEventActionMemberJoined`, *optional*):
            A new member joined the chat.

        member_joined_by_invite_link (:obj:`~pyrogram.types.ChatEventActionMemberJoinedByInviteLink`, *optional*):
            A new member joined the chat via an invite link.

        member_joined_by_request (:obj:`~pyrogram.types.ChatEventActionMemberJoinedByRequest`, *optional*):
            A new member was accepted to the chat by an administrator.

        member_invited (:obj:`~pyrogram.types.ChatEventActionMemberInvited`, *optional*):
            A new chat member was invited.

        member_left (:obj:`~pyrogram.types.ChatEventActionMemberLeft`, *optional*):
            A member left the chat.

        member_promoted (:obj:`~pyrogram.types.ChatEventActionMemberPromoted`, *optional*):
            A chat member has gained/lost administrator status, or the list of their administrator privileges has changed.

        member_restricted (:obj:`~pyrogram.types.ChatEventActionMemberRestricted`, *optional*):
            A chat member was restricted/unrestricted or banned/unbanned, or the list of their restrictions has changed.

        member_tag_changed (:obj:`~pyrogram.types.ChatEventActionMemberTagChanged`, *optional*):
            A chat member tag has been changed.

        member_subscription_extended (:obj:`~pyrogram.types.ChatEventActionMemberSubscriptionExtended`, *optional*):
            A chat member extended their subscription to the chat.

        available_reactions_changed (:obj:`~pyrogram.types.ChatEventActionAvailableReactionsChanged`, *optional*):
            The chat available reactions were changed.

        background_changed (:obj:`~pyrogram.types.ChatEventActionBackgroundChanged`, *optional*):
            The chat background was changed.

        description_changed (:obj:`~pyrogram.types.ChatEventActionDescriptionChanged`, *optional*):
            The chat description was changed.

        emoji_status_changed (:obj:`~pyrogram.types.ChatEventActionEmojiStatusChanged`, *optional*):
            The chat emoji status was changed.

        linked_chat_changed (:obj:`~pyrogram.types.ChatEventActionLinkedChatChanged`, *optional*):
            The linked chat of a supergroup was changed.

        location_changed (:obj:`~pyrogram.types.ChatEventActionLocationChanged`, *optional*):
            The supergroup location was changed.

        message_auto_delete_time_changed (:obj:`~pyrogram.types.ChatEventActionMessageAutoDeleteTimeChanged`, *optional*):
            The message auto-delete timer was changed.

        permissions_changed (:obj:`~pyrogram.types.ChatEventActionPermissionsChanged`, *optional*):
            The chat permissions were changed.

        photo_changed (:obj:`~pyrogram.types.ChatEventActionPhotoChanged`, *optional*):
            The chat photo was changed.

        slow_mode_delay_changed (:obj:`~pyrogram.types.ChatEventActionSlowModeDelayChanged`, *optional*):
            The slow_mode_delay setting of a supergroup was changed.

        sticker_set_changed (:obj:`~pyrogram.types.ChatEventActionStickerSetChanged`, *optional*):
            The supergroup sticker set was changed.

        custom_emoji_sticker_set_changed (:obj:`~pyrogram.types.ChatEventActionCustomEmojiStickerSetChanged`, *optional*):
            The supergroup sticker set with allowed custom emoji was changed.

        title_changed (:obj:`~pyrogram.types.ChatEventActionTitleChanged`, *optional*):
            The chat title was changed.

        username_changed (:obj:`~pyrogram.types.ChatEventActionUsernameChanged`, *optional*):
            The chat editable username was changed.

        active_usernames_changed (:obj:`~pyrogram.types.ChatEventActionActiveUsernamesChanged`, *optional*):
            The chat active usernames were changed.

        accent_color_changed (:obj:`~pyrogram.types.ChatEventActionAccentColorChanged`, *optional*):
            The chat accent color or background custom emoji were changed.

        profile_accent_color_changed (:obj:`~pyrogram.types.ChatEventActionProfileAccentColorChanged`, *optional*):
            The chat's profile accent color or profile background custom emoji were changed.

        has_protected_content_toggled (:obj:`~pyrogram.types.ChatEventActionHasProtectedContentToggled`, *optional*):
            The has_protected_content setting of a chat was toggled.

        invites_toggled (:obj:`~pyrogram.types.ChatEventActionInvitesToggled`, *optional*):
            The can_invite_users permission of a supergroup chat was toggled.

        is_all_history_available_toggled (:obj:`~pyrogram.types.ChatEventActionIsAllHistoryAvailableToggled`, *optional*):
            The is_all_history_available setting of a supergroup was toggled.

        has_aggressive_anti_spam_enabled_toggled (:obj:`~pyrogram.types.ChatEventActionHasAggressiveAntiSpamEnabledToggled`, *optional*):
            The has_aggressive_anti_spam_enabled setting of a supergroup was toggled.

        sign_messages_toggled (:obj:`~pyrogram.types.ChatEventActionSignMessagesToggled`, *optional*):
            The sign_messages setting of a channel was toggled.

        show_message_sender_toggled (:obj:`~pyrogram.types.ChatEventActionShowMessageSenderToggled`, *optional*):
            The show_message_sender setting of a channel was toggled.

        automatic_translation_toggled (:obj:`~pyrogram.types.ChatEventActionAutomaticTranslationToggled`, *optional*):
            The has_automatic_translation setting of a channel was toggled.

        invite_link_edited (:obj:`~pyrogram.types.ChatEventActionInviteLinkEdited`, *optional*):
            A chat invite link was edited.

        invite_link_revoked (:obj:`~pyrogram.types.ChatEventActionInviteLinkRevoked`, *optional*):
            A chat invite link was revoked.

        invite_link_deleted (:obj:`~pyrogram.types.ChatEventActionInviteLinkDeleted`, *optional*):
            A chat invite link was deleted.

        video_chat_created (:obj:`~pyrogram.types.ChatEventActionVideoChatCreated`, *optional*):
            A video chat was created.

        video_chat_ended (:obj:`~pyrogram.types.ChatEventActionVideoChatEnded`, *optional*):
            A video chat was ended.

        video_chat_mute_new_participants_toggled (:obj:`~pyrogram.types.ChatEventActionVideoChatMuteNewParticipantsToggled`, *optional*):
            The mute_new_participants setting of a video chat was toggled.

        video_chat_participant_is_muted_toggled (:obj:`~pyrogram.types.ChatEventActionVideoChatParticipantIsMutedToggled`, *optional*):
            A video chat participant was muted or unmuted.

        video_chat_participant_volume_level_changed (:obj:`~pyrogram.types.ChatEventActionVideoChatParticipantVolumeLevelChanged`, *optional*):
            A video chat participant volume level was changed.

        is_forum_toggled (:obj:`~pyrogram.types.ChatEventActionIsForumToggled`, *optional*):
            The is_forum setting of a supergroup was toggled.

        forum_topic_created (:obj:`~pyrogram.types.ChatEventActionForumTopicCreated`, *optional*):
            A new forum topic was created.

        forum_topic_edited (:obj:`~pyrogram.types.ChatEventActionForumTopicEdited`, *optional*):
            A forum topic was edited.

        forum_topic_toggle_is_closed (:obj:`~pyrogram.types.ChatEventActionForumTopicToggleIsClosed`, *optional*):
            A forum topic was closed or reopened.

        forum_topic_toggle_is_hidden (:obj:`~pyrogram.types.ChatEventActionForumTopicToggleIsHidden`, *optional*):
            The General forum topic was hidden or unhidden.

        forum_topic_deleted (:obj:`~pyrogram.types.ChatEventActionForumTopicDeleted`, *optional*):
            A forum topic was deleted.

        forum_topic_pinned (:obj:`~pyrogram.types.ChatEventActionForumTopicPinned`, *optional*):
            A pinned forum topic was changed.

        raw (:obj:`~pyrogram.raw.base.ChannelAdminLogEvent`, *optional*):
            A raw object.
    """

    def __init__(
        self,
        *,
        id: int,
        date: datetime,
        member: types.Chat,
        action: enums.ChatEventActionType,
        message_edited: types.ChatEventActionMessageEdited | None = None,
        message_deleted: types.ChatEventActionMessageDeleted | None = None,
        message_pinned: types.ChatEventActionMessagePinned | None = None,
        message_unpinned: types.ChatEventActionMessageUnpinned | None = None,
        poll_stopped: types.ChatEventActionPollStopped | None = None,
        member_joined: types.ChatEventActionMemberJoined | None = None,
        member_joined_by_invite_link: types.ChatEventActionMemberJoinedByInviteLink | None = None,
        member_joined_by_request: types.ChatEventActionMemberJoinedByRequest | None = None,
        member_invited: types.ChatEventActionMemberInvited | None = None,
        member_left: types.ChatEventActionMemberLeft | None = None,
        member_promoted: types.ChatEventActionMemberPromoted | None = None,
        member_restricted: types.ChatEventActionMemberRestricted | None = None,
        member_tag_changed: types.ChatEventActionMemberTagChanged | None = None,
        member_subscription_extended: types.ChatEventActionMemberSubscriptionExtended | None = None,
        available_reactions_changed: types.ChatEventActionAvailableReactionsChanged | None = None,
        background_changed: types.ChatEventActionBackgroundChanged | None = None,
        description_changed: types.ChatEventActionDescriptionChanged | None = None,
        emoji_status_changed: types.ChatEventActionEmojiStatusChanged | None = None,
        linked_chat_changed: types.ChatEventActionLinkedChatChanged | None = None,
        location_changed: types.ChatEventActionLocationChanged | None = None,
        message_auto_delete_time_changed: types.ChatEventActionMessageAutoDeleteTimeChanged
        | None = None,
        permissions_changed: types.ChatEventActionPermissionsChanged | None = None,
        photo_changed: types.ChatEventActionPhotoChanged | None = None,
        slow_mode_delay_changed: types.ChatEventActionSlowModeDelayChanged | None = None,
        sticker_set_changed: types.ChatEventActionStickerSetChanged | None = None,
        custom_emoji_sticker_set_changed: types.ChatEventActionCustomEmojiStickerSetChanged
        | None = None,
        title_changed: types.ChatEventActionTitleChanged | None = None,
        username_changed: types.ChatEventActionUsernameChanged | None = None,
        active_usernames_changed: types.ChatEventActionActiveUsernamesChanged | None = None,
        accent_color_changed: types.ChatEventActionAccentColorChanged | None = None,
        profile_accent_color_changed: types.ChatEventActionProfileAccentColorChanged | None = None,
        has_protected_content_toggled: types.ChatEventActionHasProtectedContentToggled
        | None = None,
        invites_toggled: types.ChatEventActionInvitesToggled | None = None,
        is_all_history_available_toggled: types.ChatEventActionIsAllHistoryAvailableToggled
        | None = None,
        has_aggressive_anti_spam_enabled_toggled: types.ChatEventActionHasAggressiveAntiSpamEnabledToggled
        | None = None,
        sign_messages_toggled: types.ChatEventActionSignMessagesToggled | None = None,
        show_message_sender_toggled: types.ChatEventActionShowMessageSenderToggled | None = None,
        automatic_translation_toggled: types.ChatEventActionAutomaticTranslationToggled
        | None = None,
        invite_link_edited: types.ChatEventActionInviteLinkEdited | None = None,
        invite_link_revoked: types.ChatEventActionInviteLinkRevoked | None = None,
        invite_link_deleted: types.ChatEventActionInviteLinkDeleted | None = None,
        video_chat_created: types.ChatEventActionVideoChatCreated | None = None,
        video_chat_ended: types.ChatEventActionVideoChatEnded | None = None,
        video_chat_mute_new_participants_toggled: types.ChatEventActionVideoChatMuteNewParticipantsToggled
        | None = None,
        video_chat_participant_is_muted_toggled: types.ChatEventActionVideoChatParticipantIsMutedToggled
        | None = None,
        video_chat_participant_volume_level_changed: types.ChatEventActionVideoChatParticipantVolumeLevelChanged
        | None = None,
        is_forum_toggled: types.ChatEventActionIsForumToggled | None = None,
        forum_topic_created: types.ChatEventActionForumTopicCreated | None = None,
        forum_topic_edited: types.ChatEventActionForumTopicEdited | None = None,
        forum_topic_toggle_is_closed: types.ChatEventActionForumTopicToggleIsClosed | None = None,
        forum_topic_toggle_is_hidden: types.ChatEventActionForumTopicToggleIsHidden | None = None,
        forum_topic_deleted: types.ChatEventActionForumTopicDeleted | None = None,
        forum_topic_pinned: types.ChatEventActionForumTopicPinned | None = None,
        raw: raw.base.ChannelAdminLogEvent | None = None,
    ):
        super().__init__()

        self.id = id
        self.date = date
        self.member = member
        self.action = action
        self.message_edited = message_edited
        self.message_deleted = message_deleted
        self.message_pinned = message_pinned
        self.message_unpinned = message_unpinned
        self.poll_stopped = poll_stopped
        self.member_joined = member_joined
        self.member_joined_by_invite_link = member_joined_by_invite_link
        self.member_joined_by_request = member_joined_by_request
        self.member_invited = member_invited
        self.member_left = member_left
        self.member_promoted = member_promoted
        self.member_restricted = member_restricted
        self.member_tag_changed = member_tag_changed
        self.member_subscription_extended = member_subscription_extended
        self.available_reactions_changed = available_reactions_changed
        self.background_changed = background_changed
        self.description_changed = description_changed
        self.emoji_status_changed = emoji_status_changed
        self.linked_chat_changed = linked_chat_changed
        self.location_changed = location_changed
        self.message_auto_delete_time_changed = message_auto_delete_time_changed
        self.permissions_changed = permissions_changed
        self.photo_changed = photo_changed
        self.slow_mode_delay_changed = slow_mode_delay_changed
        self.sticker_set_changed = sticker_set_changed
        self.custom_emoji_sticker_set_changed = custom_emoji_sticker_set_changed
        self.title_changed = title_changed
        self.username_changed = username_changed
        self.active_usernames_changed = active_usernames_changed
        self.accent_color_changed = accent_color_changed
        self.profile_accent_color_changed = profile_accent_color_changed
        self.has_protected_content_toggled = has_protected_content_toggled
        self.invites_toggled = invites_toggled
        self.is_all_history_available_toggled = is_all_history_available_toggled
        self.has_aggressive_anti_spam_enabled_toggled = has_aggressive_anti_spam_enabled_toggled
        self.sign_messages_toggled = sign_messages_toggled
        self.show_message_sender_toggled = show_message_sender_toggled
        self.automatic_translation_toggled = automatic_translation_toggled
        self.invite_link_edited = invite_link_edited
        self.invite_link_revoked = invite_link_revoked
        self.invite_link_deleted = invite_link_deleted
        self.video_chat_created = video_chat_created
        self.video_chat_ended = video_chat_ended
        self.video_chat_mute_new_participants_toggled = video_chat_mute_new_participants_toggled
        self.video_chat_participant_is_muted_toggled = video_chat_participant_is_muted_toggled
        self.video_chat_participant_volume_level_changed = (
            video_chat_participant_volume_level_changed
        )
        self.is_forum_toggled = is_forum_toggled
        self.forum_topic_created = forum_topic_created
        self.forum_topic_edited = forum_topic_edited
        self.forum_topic_toggle_is_closed = forum_topic_toggle_is_closed
        self.forum_topic_toggle_is_hidden = forum_topic_toggle_is_hidden
        self.forum_topic_deleted = forum_topic_deleted
        self.forum_topic_pinned = forum_topic_pinned

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        event: raw.base.ChannelAdminLogEvent,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ):
        action = event.action
        action_type = enums.ChatEventActionType.UNSUPPORTED

        message_edited = None
        message_deleted = None
        message_pinned = None
        message_unpinned = None
        poll_stopped = None
        member_joined = None
        member_joined_by_invite_link = None
        member_joined_by_request = None
        member_invited = None
        member_left = None
        member_promoted = None
        member_restricted = None
        member_tag_changed = None
        member_subscription_extended = None
        available_reactions_changed = None
        background_changed = None
        description_changed = None
        emoji_status_changed = None
        linked_chat_changed = None
        location_changed = None
        message_auto_delete_time_changed = None
        permissions_changed = None
        photo_changed = None
        slow_mode_delay_changed = None
        sticker_set_changed = None
        custom_emoji_sticker_set_changed = None
        title_changed = None
        username_changed = None
        active_usernames_changed = None
        accent_color_changed = None
        profile_accent_color_changed = None
        has_protected_content_toggled = None
        invites_toggled = None
        is_all_history_available_toggled = None
        has_aggressive_anti_spam_enabled_toggled = None
        sign_messages_toggled = None
        show_message_sender_toggled = None
        automatic_translation_toggled = None
        invite_link_edited = None
        invite_link_revoked = None
        invite_link_deleted = None
        video_chat_created = None
        video_chat_ended = None
        video_chat_mute_new_participants_toggled = None
        video_chat_participant_is_muted_toggled = None
        video_chat_participant_volume_level_changed = None
        is_forum_toggled = None
        forum_topic_created = None
        forum_topic_edited = None
        forum_topic_toggle_is_closed = None
        forum_topic_toggle_is_hidden = None
        forum_topic_deleted = None
        forum_topic_pinned = None

        if isinstance(action, raw.types.ChannelAdminLogEventActionEditMessage):
            action_type = enums.ChatEventActionType.MESSAGE_EDITED
            message_edited = types.ChatEventActionMessageEdited(
                old_message=await types.Message._parse(client, action.prev_message, users, chats),
                new_message=await types.Message._parse(client, action.new_message, users, chats),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionDeleteMessage):
            action_type = enums.ChatEventActionType.MESSAGE_DELETED

            if client._app_config is not None:
                app_config: dict = utils.jsonvalue_to_obj(client._app_config.config)
            else:
                app_config: dict = await client.get_app_config()

            message_deleted = types.ChatEventActionMessageDeleted(
                message=await types.Message._parse(client, action.message, users, chats),
                can_report_anti_spam_false_positive=event.user_id
                == int(app_config["telegram_antispam_user_id"])
                if app_config.get("telegram_antispam_user_id")
                else False,
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionUpdatePinned):
            if action.message.pinned:
                action_type = enums.ChatEventActionType.MESSAGE_PINNED
                message_pinned = types.ChatEventActionMessagePinned(
                    message=await types.Message._parse(client, action.message, users, chats)
                )
            else:
                action_type = enums.ChatEventActionType.MESSAGE_UNPINNED
                message_unpinned = types.ChatEventActionMessageUnpinned(
                    message=await types.Message._parse(client, action.message, users, chats)
                )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionStopPoll):
            action_type = enums.ChatEventActionType.POLL_STOPPED
            poll_stopped = types.ChatEventActionPollStopped(
                message=await types.Message._parse(client, action.message, users, chats)
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantJoin):
            action_type = enums.ChatEventActionType.MEMBER_JOINED
            member_joined = types.ChatEventActionMemberJoined()
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantJoinByInvite):
            action_type = enums.ChatEventActionType.MEMBER_JOINED_BY_INVITE_LINK
            member_joined_by_invite_link = types.ChatEventActionMemberJoinedByInviteLink(
                invite_link=await types.ChatInviteLink._parse(client, action.invite, users),
                via_chat_folder_invite_link=action.via_chatlist,
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantJoinByRequest):
            action_type = enums.ChatEventActionType.MEMBER_JOINED_BY_REQUEST
            member_joined_by_invite_link = types.ChatEventActionMemberJoinedByRequest(
                approver_user=await types.User._parse(client, users.get(action.approved_by)),
                invite_link=await types.ChatInviteLink._parse(client, action.invite, users),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantInvite):
            action_type = enums.ChatEventActionType.MEMBER_INVITED
            member_invited = types.ChatEventActionMemberInvited(
                member=await types.ChatMember._parse(client, event.action.participant, users, chats)
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantLeave):
            action_type = enums.ChatEventActionType.MEMBER_LEFT
            member_left = types.ChatEventActionMemberLeft()
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantToggleAdmin):
            action_type = enums.ChatEventActionType.MEMBER_PROMOTED
            member_promoted = types.ChatEventActionMemberPromoted(
                old_member=await types.ChatMember._parse(
                    client, action.prev_participant, users, chats
                ),
                new_member=await types.ChatMember._parse(
                    client, action.new_participant, users, chats
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantToggleBan):
            action_type = enums.ChatEventActionType.MEMBER_RESTRICTED
            member_restricted = types.ChatEventActionMemberRestricted(
                old_member=await types.ChatMember._parse(
                    client, action.prev_participant, users, chats
                ),
                new_member=await types.ChatMember._parse(
                    client, action.new_participant, users, chats
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantEditRank):
            action_type = enums.ChatEventActionType.MEMBER_TAG_CHANGED
            member_tag_changed = types.ChatEventActionMemberTagChanged(
                user=await types.User._parse(client=client, user=users[action.user_id]),
                old_tag=action.prev_rank,
                new_tag=action.new_rank,
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantSubExtend):
            action_type = enums.ChatEventActionType.MEMBER_SUBSCRIPTION_EXTENDED
            member_subscription_extended = types.ChatEventActionMemberSubscriptionExtended(
                old_member=await types.ChatMember._parse(
                    client, action.prev_participant, users, chats
                ),
                new_member=await types.ChatMember._parse(
                    client, action.new_participant, users, chats
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeAvailableReactions):
            action_type = enums.ChatEventActionType.AVAILABLE_REACTIONS_CHANGED
            available_reactions_changed = types.ChatEventActionAvailableReactionsChanged(
                old_available_reactions=types.ChatReactions._parse(
                    client=client, chat_reactions=action.prev_value
                ),
                new_available_reactions=types.ChatReactions._parse(
                    client=client, chat_reactions=action.new_value
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeWallpaper):
            action_type = enums.ChatEventActionType.BACKGROUND_CHANGED
            available_reactions_changed = types.ChatEventActionBackgroundChanged(
                old_background=types.ChatBackground._parse(
                    client=client, background=action.prev_value
                ),
                new_background=types.ChatBackground._parse(
                    client=client, background=action.new_value
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeAbout):
            action_type = enums.ChatEventActionType.DESCRIPTION_CHANGED
            description_changed = types.ChatEventActionDescriptionChanged(
                old_description=action.prev_value, new_description=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeEmojiStatus):
            action_type = enums.ChatEventActionType.EMOJI_STATUS_CHANGED
            emoji_status_changed = types.ChatEventActionEmojiStatusChanged(
                old_emoji_status=types.EmojiStatus._parse(
                    client=client, emoji_status=action.prev_value
                ),
                new_emoji_status=types.EmojiStatus._parse(
                    client=client, emoji_status=action.new_value
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeLinkedChat):
            action_type = enums.ChatEventActionType.LINKED_CHAT_CHANGED
            linked_chat_changed = types.ChatEventActionLinkedChatChanged(
                old_linked_chat=await types.Chat._parse_chat(
                    client=client, chat=chats.get(action.prev_value)
                ),
                new_linked_chat=await types.Chat._parse_chat(
                    client=client, chat=chats.get(action.new_value)
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeLocation):
            action_type = enums.ChatEventActionType.LOCATION_CHANGED
            location_changed = types.ChatEventActionLocationChanged(
                old_location=types.Location._parse(geo_point=action.prev_value),
                new_location=types.Location._parse(geo_point=action.new_value),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeHistoryTTL):
            action_type = enums.ChatEventActionType.MESSAGE_AUTO_DELETE_TIME_CHANGED
            message_auto_delete_time_changed = types.ChatEventActionMessageAutoDeleteTimeChanged(
                old_message_auto_delete_time=action.prev_value,
                new_message_auto_delete_time=action.new_value,
            )

        elif isinstance(action, raw.types.ChannelAdminLogEventActionDefaultBannedRights):
            action_type = enums.ChatEventActionType.PERMISSIONS_CHANGED
            permissions_changed = types.ChatEventActionPermissionsChanged(
                old_permissions=types.ChatPermissions._parse(
                    denied_permissions=action.prev_banned_rights
                ),
                new_permissions=types.ChatPermissions._parse(
                    denied_permissions=action.new_banned_rights
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangePhoto):
            action_type = enums.ChatEventActionType.PHOTO_CHANGED
            photo_changed = types.ChatEventActionPhotoChanged(
                old_photo=types.Photo._parse(client, action.prev_photo),
                new_photo=types.Photo._parse(client, action.new_photo),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionToggleSlowMode):
            action_type = enums.ChatEventActionType.SLOW_MODE_DELAY_CHANGED
            slow_mode_delay_changed = types.ChatEventActionSlowModeDelayChanged(
                old_slow_mode_delay=action.prev_value, new_slow_mode_delay=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeStickerSet):
            action_type = enums.ChatEventActionType.STICKER_SET_CHANGED
            sticker_set_changed = types.ChatEventActionStickerSetChanged(
                old_sticker_set_id=getattr(action.prev_stickerset, "id", None),
                new_sticker_set_id=getattr(action.new_stickerset, "id", None),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeStickerSet):
            action_type = enums.ChatEventActionType.STICKER_SET_CHANGED
            custom_emoji_sticker_set_changed = types.ChatEventActionCustomEmojiStickerSetChanged(
                old_sticker_set_id=getattr(action.prev_stickerset, "id", None),
                new_sticker_set_id=getattr(action.new_stickerset, "id", None),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeTitle):
            action_type = enums.ChatEventActionType.TITLE_CHANGED
            title_changed = types.ChatEventActionTitleChanged(
                old_title=action.prev_value, new_title=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeUsername):
            action_type = enums.ChatEventActionType.USERNAME_CHANGED
            username_changed = types.ChatEventActionUsernameChanged(
                old_username=action.prev_value, new_username=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeUsernames):
            action_type = enums.ChatEventActionType.ACTIVE_USERNAMES_CHANGED
            username_changed = types.ChatEventActionActiveUsernamesChanged(
                old_usernames=action.prev_value, new_usernames=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangePeerColor):
            action_type = enums.ChatEventActionType.ACCENT_COLOR_CHANGED
            accent_color_changed = types.ChatEventActionAccentColorChanged(
                old_accent_color_id=getattr(action.prev_value, "color", None),
                old_background_custom_emoji_id=str(action.prev_value.custom_emoji_id)
                if getattr(action.prev_value, "custom_emoji_id", None)
                else None,
                new_accent_color_id=getattr(action.new_value, "color", None),
                new_background_custom_emoji_id=str(action.new_value.custom_emoji_id)
                if getattr(action.new_value, "custom_emoji_id", None)
                else None,
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionChangeProfilePeerColor):
            action_type = enums.ChatEventActionType.PROFILE_ACCENT_COLOR_CHANGED
            profile_accent_color_changed = types.ChatEventActionProfileAccentColorChanged(
                old_profile_accent_color_id=getattr(action.prev_value, "color", None),
                old_profile_background_custom_emoji_id=str(action.prev_value.custom_emoji_id)
                if getattr(action.prev_value, "custom_emoji_id", None)
                else None,
                new_profile_accent_color_id=getattr(action.new_value, "color", None),
                new_profile_background_custom_emoji_id=str(action.new_value.custom_emoji_id)
                if getattr(action.new_value, "custom_emoji_id", None)
                else None,
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionToggleNoForwards):
            action_type = enums.ChatEventActionType.HAS_PROTECTED_CONTENT_TOGGLED
            has_protected_content_toggled = types.ChatEventActionHasProtectedContentToggled(
                has_protected_content=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionToggleInvites):
            action_type = enums.ChatEventActionType.INVITES_TOGGLED
            invites_toggled = types.ChatEventActionInvitesToggled(can_invite_users=action.new_value)
        elif isinstance(action, raw.types.ChannelAdminLogEventActionTogglePreHistoryHidden):
            action_type = enums.ChatEventActionType.IS_ALL_HISTORY_AVAILABLE_TOGGLED
            is_all_history_available_toggled = types.ChatEventActionIsAllHistoryAvailableToggled(
                is_all_history_available=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionToggleAntiSpam):
            action_type = enums.ChatEventActionType.HAS_AGGRESSIVE_ANTI_SPAM_ENABLED_TOGGLED
            has_aggressive_anti_spam_enabled_toggled = (
                types.ChatEventActionHasAggressiveAntiSpamEnabledToggled(
                    has_aggressive_anti_spam_enabled=action.new_value
                )
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionToggleSignatures):
            action_type = enums.ChatEventActionType.SIGN_MESSAGES_TOGGLED
            has_aggressive_anti_spam_enabled_toggled = types.ChatEventActionSignMessagesToggled(
                sign_messages=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionToggleSignatureProfiles):
            action_type = enums.ChatEventActionType.SHOW_MESSAGE_SENDER_TOGGLED
            show_message_sender_toggled = types.ChatEventActionShowMessageSenderToggled(
                show_message_sender=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionToggleAutotranslation):
            action_type = enums.ChatEventActionType.AUTOMATIC_TRANSLATION_TOGGLED
            automatic_translation_toggled = types.ChatEventActionAutomaticTranslationToggled(
                has_automatic_translation=action.new_value
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionExportedInviteEdit):
            action_type = enums.ChatEventActionType.INVITE_LINK_EDITED
            invite_link_edited = types.ChatEventActionInviteLinkEdited(
                old_invite_link=types.ChatInviteLink._parse(
                    client=client, invite=action.prev_invite, users=users
                ),
                new_invite_link=types.ChatInviteLink._parse(
                    client=client, invite=action.new_invite, users=users
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionExportedInviteRevoke):
            action_type = enums.ChatEventActionType.INVITE_LINK_REVOKED
            invite_link_revoked = types.ChatEventActionInviteLinkRevoked(
                invite_link=types.ChatInviteLink._parse(
                    client=client, invite=action.invite, users=users
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionExportedInviteDelete):
            action_type = enums.ChatEventActionType.INVITE_LINK_DELETED
            invite_link_deleted = types.ChatEventActionInviteLinkDeleted(
                invite_link=types.ChatInviteLink._parse(
                    client=client, invite=action.invite, users=users
                ),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionStartGroupCall):
            action_type = enums.ChatEventActionType.VIDEO_CHAT_CREATED
            video_chat_created = types.ChatEventActionVideoChatCreated(
                group_call_id=getattr(action.call, "id", None),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionDiscardGroupCall):
            action_type = enums.ChatEventActionType.VIDEO_CHAT_ENDED
            video_chat_ended = types.ChatEventActionVideoChatEnded(
                group_call_id=getattr(action.call, "id", None),
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionToggleGroupCallSetting):
            action_type = enums.ChatEventActionType.VIDEO_CHAT_MUTE_NEW_PARTICIPANTS_TOGGLED
            video_chat_mute_new_participants_toggled = (
                types.ChatEventActionVideoChatMuteNewParticipantsToggled(
                    mute_new_participants=action.join_muted,
                )
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantMute):
            action_type = enums.ChatEventActionType.VIDEO_CHAT_PARTICIPANT_IS_MUTED_TOGGLED
            participant_id = utils.get_raw_peer_id(action.participant.peer)
            video_chat_participant_is_muted_toggled = (
                types.ChatEventActionVideoChatParticipantIsMutedToggled(
                    participant=await types.Chat._parse_chat(
                        client=client, chat=users.get(participant_id) or chats.get(participant_id)
                    ),
                    is_muted=True,
                )
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantUnmute):
            action_type = enums.ChatEventActionType.VIDEO_CHAT_PARTICIPANT_IS_MUTED_TOGGLED
            participant_id = utils.get_raw_peer_id(action.participant.peer)
            video_chat_participant_is_muted_toggled = (
                types.ChatEventActionVideoChatParticipantIsMutedToggled(
                    participant=await types.Chat._parse_chat(
                        client=client, chat=users.get(participant_id) or chats.get(participant_id)
                    ),
                    is_muted=False,
                )
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionParticipantVolume):
            action_type = enums.ChatEventActionType.VIDEO_CHAT_PARTICIPANT_VOLUME_LEVEL_CHANGED
            participant_id = utils.get_raw_peer_id(action.participant.peer)
            video_chat_participant_volume_level_changed = (
                types.ChatEventActionVideoChatParticipantVolumeLevelChanged(
                    participant=await types.Chat._parse_chat(
                        client=client, chat=users.get(participant_id) or chats.get(participant_id)
                    ),
                    volume_level=action.participant.volume,
                )
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionToggleForum):
            action_type = enums.ChatEventActionType.IS_FORUM_TOGGLED
            is_forum_toggled = types.ChatEventActionIsForumToggled(is_forum=action.new_value)
        elif isinstance(action, raw.types.ChannelAdminLogEventActionCreateTopic):
            action_type = enums.ChatEventActionType.FORUM_TOPIC_CREATED
            forum_topic_created = types.ChatEventActionForumTopicCreated(
                topic_info=await types.ForumTopic._parse(
                    client, action.topic, users=users, chats=chats
                )
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionEditTopic):
            if action.prev_topic.closed != action.new_topic.closed:
                action_type = enums.ChatEventActionType.FORUM_TOPIC_TOGGLE_IS_CLOSED
                forum_topic_toggle_is_closed = types.ChatEventActionForumTopicToggleIsClosed(
                    topic_info=await types.ForumTopic._parse(
                        client, action.new_topic, users=users, chats=chats
                    )
                )
            elif action.prev_topic.hidden != action.new_topic.hidden:
                action_type = enums.ChatEventActionType.FORUM_TOPIC_TOGGLE_IS_HIDDEN
                forum_topic_toggle_is_hidden = types.ChatEventActionForumTopicToggleIsHidden(
                    topic_info=await types.ForumTopic._parse(
                        client, action.new_topic, users=users, chats=chats
                    )
                )
            else:
                action_type = enums.ChatEventActionType.FORUM_TOPIC_EDITED
                forum_topic_edited = types.ChatEventActionForumTopicEdited(
                    old_topic_info=await types.ForumTopic._parse(
                        client, action.prev_topic, users=users, chats=chats
                    ),
                    new_topic_info=await types.ForumTopic._parse(
                        client, action.new_topic, users=users, chats=chats
                    ),
                )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionDeleteTopic):
            action_type = enums.ChatEventActionType.FORUM_TOPIC_DELETED
            forum_topic_deleted = types.ChatEventActionForumTopicDeleted(
                topic_info=await types.ForumTopic._parse(
                    client, action.topic, users=users, chats=chats
                )
            )
        elif isinstance(action, raw.types.ChannelAdminLogEventActionPinTopic):
            action_type = enums.ChatEventActionType.FORUM_TOPIC_PINNED
            forum_topic_pinned = types.ChatEventActionForumTopicPinned(
                old_topic_info=await types.ForumTopic._parse(
                    client, action.prev_topic, users=users, chats=chats
                ),
                new_topic_info=await types.ForumTopic._parse(
                    client, action.new_topic, users=users, chats=chats
                ),
            )

        return ChatEvent(
            id=event.id,
            date=utils.timestamp_to_datetime(event.date),
            member=await types.Chat._parse_chat(
                client, users.get(event.user_id) or chats.get(event.user_id)
            ),
            action=action_type,
            message_edited=message_edited,
            message_deleted=message_deleted,
            message_pinned=message_pinned,
            message_unpinned=message_unpinned,
            poll_stopped=poll_stopped,
            member_joined=member_joined,
            member_joined_by_invite_link=member_joined_by_invite_link,
            member_joined_by_request=member_joined_by_request,
            member_invited=member_invited,
            member_left=member_left,
            member_promoted=member_promoted,
            member_restricted=member_restricted,
            member_tag_changed=member_tag_changed,
            member_subscription_extended=member_subscription_extended,
            available_reactions_changed=available_reactions_changed,
            background_changed=background_changed,
            description_changed=description_changed,
            emoji_status_changed=emoji_status_changed,
            linked_chat_changed=linked_chat_changed,
            location_changed=location_changed,
            message_auto_delete_time_changed=message_auto_delete_time_changed,
            permissions_changed=permissions_changed,
            photo_changed=photo_changed,
            slow_mode_delay_changed=slow_mode_delay_changed,
            sticker_set_changed=sticker_set_changed,
            custom_emoji_sticker_set_changed=custom_emoji_sticker_set_changed,
            title_changed=title_changed,
            username_changed=username_changed,
            active_usernames_changed=active_usernames_changed,
            accent_color_changed=accent_color_changed,
            profile_accent_color_changed=profile_accent_color_changed,
            has_protected_content_toggled=has_protected_content_toggled,
            invites_toggled=invites_toggled,
            is_all_history_available_toggled=is_all_history_available_toggled,
            has_aggressive_anti_spam_enabled_toggled=has_aggressive_anti_spam_enabled_toggled,
            sign_messages_toggled=sign_messages_toggled,
            show_message_sender_toggled=show_message_sender_toggled,
            automatic_translation_toggled=automatic_translation_toggled,
            invite_link_edited=invite_link_edited,
            invite_link_revoked=invite_link_revoked,
            invite_link_deleted=invite_link_deleted,
            video_chat_created=video_chat_created,
            video_chat_ended=video_chat_ended,
            video_chat_mute_new_participants_toggled=video_chat_mute_new_participants_toggled,
            video_chat_participant_is_muted_toggled=video_chat_participant_is_muted_toggled,
            video_chat_participant_volume_level_changed=video_chat_participant_volume_level_changed,
            is_forum_toggled=is_forum_toggled,
            forum_topic_created=forum_topic_created,
            forum_topic_edited=forum_topic_edited,
            forum_topic_toggle_is_closed=forum_topic_toggle_is_closed,
            forum_topic_toggle_is_hidden=forum_topic_toggle_is_hidden,
            forum_topic_deleted=forum_topic_deleted,
            forum_topic_pinned=forum_topic_pinned,
            raw=event,
        )
