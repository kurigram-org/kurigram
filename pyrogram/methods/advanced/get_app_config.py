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


import pyrogram
from pyrogram import raw, utils


class GetAppConfig:
    async def get_app_config(self: pyrogram.Client) -> dict:
        """Get app-specific configuration.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            ``dict``: App-specific configuration is returned.
        """
        r = await self.invoke(raw.functions.help.GetAppConfig(hash=0))

        self._app_config = r

        return utils.jsonvalue_to_obj(r.config)
