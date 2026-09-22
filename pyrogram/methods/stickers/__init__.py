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

from .add_favorite_sticker import AddFavoriteSticker
from .add_recent_sticker import AddRecentSticker
from .add_sticker_to_set import AddStickerToSet
from .change_sticker_set import ChangeStickerSet
from .clear_recent_stickers import ClearRecentStickers
from .create_new_sticker_set import CreateNewStickerSet
from .delete_sticker_from_set import DeleteStickerFromSet
from .delete_sticker_set import DeleteStickerSet
from .get_custom_emoji_stickers import GetCustomEmojiStickers
from .get_favorite_stickers import GetFavoriteStickers
from .get_owned_sticker_sets import GetOwnedStickerSets
from .get_recent_stickers import GetRecentStickers
from .get_sticker_set import GetStickerSet
from .get_suggested_sticker_set_name import GetSuggestedStickerSetName
from .remove_favorite_sticker import RemoveFavoriteSticker
from .remove_recent_sticker import RemoveRecentSticker
from .reorder_installed_sticker_sets import ReorderInstalledStickerSets
from .replace_sticker_in_set import ReplaceStickerInSet
from .search_sticker_sets import SearchStickerSets
from .search_stickers import SearchStickers
from .set_custom_emoji_sticker_set_thumbnail import SetCustomEmojiStickerSetThumbnail
from .set_sticker_emoji_list import SetStickerEmojiList
from .set_sticker_keywords import SetStickerKeywords
from .set_sticker_mask_position import SetStickerMaskPosition
from .set_sticker_position_in_set import SetStickerPositionInSet
from .set_sticker_set_thumbnail import SetStickerSetThumbnail
from .set_sticker_set_title import SetStickerSetTitle
from .upload_sticker_file import UploadStickerFile


class Stickers(
    AddFavoriteSticker,
    AddRecentSticker,
    AddStickerToSet,
    ChangeStickerSet,
    ClearRecentStickers,
    CreateNewStickerSet,
    DeleteStickerFromSet,
    DeleteStickerSet,
    GetCustomEmojiStickers,
    GetFavoriteStickers,
    GetOwnedStickerSets,
    GetRecentStickers,
    GetStickerSet,
    GetSuggestedStickerSetName,
    RemoveFavoriteSticker,
    RemoveRecentSticker,
    ReorderInstalledStickerSets,
    ReplaceStickerInSet,
    SearchStickerSets,
    SearchStickers,
    SetCustomEmojiStickerSetThumbnail,
    SetStickerEmojiList,
    SetStickerKeywords,
    SetStickerMaskPosition,
    SetStickerPositionInSet,
    SetStickerSetThumbnail,
    SetStickerSetTitle,
    UploadStickerFile,
):
    pass
