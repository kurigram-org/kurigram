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

from ..object import Object


class UniqueGiftBackdropColors(Object):
    """This object describes the colors of the backdrop of a unique gift.

    Parameters:
        center_color (``int``):
            The color in the center of the backdrop in RGB format.

        edge_color (``int``):
            The color on the edges of the backdrop in RGB format.

        symbol_color (``int``):
            The color to be applied to the symbol in RGB format.

        text_color (``int``):
            The color for the text on the backdrop in RGB format.
    """

    def __init__(
        self, *, center_color: int, edge_color: int, symbol_color: int, text_color: int
    ) -> None:
        super().__init__()

        self.center_color = center_color
        self.edge_color = edge_color
        self.symbol_color = symbol_color
        self.text_color = text_color
