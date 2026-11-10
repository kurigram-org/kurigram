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

from typing import TYPE_CHECKING

import pyrogram
from pyrogram.filters import Filter
from .unbound_arguments import unbound_arguments

if TYPE_CHECKING:
    from collections.abc import Callable

    from .handler_type import HandlerType


class OnWidgetQuery:
    def on_widget_query(
        self: OnWidgetQuery | Filter | None = None,
        filters: Filter | None = None,
        group: int = 0,
    ) -> Callable[[HandlerType], HandlerType]:
        """Decorator for handling widget queries.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.WidgetQueryHandler`.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of widget queries to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: HandlerType) -> HandlerType:
            if isinstance(self, pyrogram.Client):
                self.add_handler(pyrogram.handlers.WidgetQueryHandler(func, filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                arguments = unbound_arguments(self, filters=filters, group=group)

                func.handlers.append(
                    (pyrogram.handlers.WidgetQueryHandler(func, arguments.filters), arguments.group)
                )

            return func

        return decorator
