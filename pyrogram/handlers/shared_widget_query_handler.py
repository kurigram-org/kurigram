#  Kurigram - Telegram MTProto API Client Library for Python
#
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2024-present KurimuzonAkuma <https://github.com/KurimuzonAkuma>
#
#  This file is part of Kurigram.
#
#  Kurigram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Kurigram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Kurigram. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pyrogram import types

from .handler import Handler

if TYPE_CHECKING:
    import pyrogram
    from pyrogram.filters import Filter

SharedWidgetQueryCallbackType = Callable[["pyrogram.Client", types.SharedWidgetQuery], Any]


class SharedWidgetQueryHandler(Handler[SharedWidgetQueryCallbackType]):
    """The SharedWidgetQuery handler class. Used to handle shared widget queries.
    It is intended to be used with :meth:`~pyrogram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyrogram.Client.on_shared_widget_query` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new SharedWidgetQuery arrives. It takes *(client, shared_widget_query)*
            as positional arguments (look at the section below for a detailed description).

        filters (:obj:`~pyrogram.filters.Filter`):
            Pass one or more filters to allow only a subset of shared widget queries to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyrogram.Client`):
            The Client itself, useful when you want to call other API methods inside the shared widget query handler.

        shared_widget_query (:obj:`~pyrogram.types.SharedWidgetQuery`):
            The received shared widget query.
    """

    def __init__(
        self, callback: SharedWidgetQueryCallbackType, filters: Filter | None = None
    ) -> None:
        super().__init__(callback, filters)
