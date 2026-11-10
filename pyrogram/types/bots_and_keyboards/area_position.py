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

from ..object import Object

if TYPE_CHECKING:
    from pyrogram import raw


class AreaPosition(Object):
    """Describes the position of a rectangle area on a story media or a TON wallet card.

    Parameters:
        x_percentage (``float``):
            The abscissa of the area's center, as a percentage of the media or the card width.

        y_percentage (``float``):
            The ordinate of the area's center, as a percentage of the media or the card height.

        width_percentage (``float``):
            The width of the area's rectangle, as a percentage of the media or the card width.

        height_percentage (``float``):
            The height of the area's rectangle, as a percentage of the media or the card height.

        rotation_angle (``float``):
            The clockwise rotation angle of the rectangle, in degrees, 0-360.

        corner_radius_percentage (``float``):
            The radius of the rectangle corner rounding, as a percentage of the media or the card width.
    """

    def __init__(
        self,
        *,
        x_percentage: float,
        y_percentage: float,
        width_percentage: float,
        height_percentage: float,
        rotation_angle: float,
        corner_radius_percentage: float,
    ) -> None:
        super().__init__()

        self.x_percentage = x_percentage
        self.y_percentage = y_percentage
        self.width_percentage = width_percentage
        self.height_percentage = height_percentage
        self.rotation_angle = rotation_angle
        self.corner_radius_percentage = corner_radius_percentage

    @staticmethod
    def _parse(coordinates: raw.types.MediaAreaCoordinates) -> AreaPosition:
        return AreaPosition(
            x_percentage=coordinates.x,
            y_percentage=coordinates.y,
            width_percentage=coordinates.w,
            height_percentage=coordinates.h,
            rotation_angle=coordinates.rotation,
            corner_radius_percentage=coordinates.radius or 0.0,
        )
