from math import cos, sin, radians

from geometry import (
    Point,
    MultiPoint,
    Polygon,
    MultiPolygon,
    LineString,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    create_straight_rectangle,
    prepare,
    distance,

    OrientedPoint,
    nearest_points,
    box
)
from logger import Logger, LogLevels
import numpy as np

from arena.grid_manager import GridManager
from arena.arena_zone import (
    ZoneType, BaseArenaZone,
    EnemyZone,
    StuffZone,
    ForbiddenZone,
    BlueReservedZone, YellowReservedZone,
    BorderZone
)

import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry


class Arena2:
    """
    All distances are in cm.
    """

    def __init__(self,
                 logger: Logger,
                 width: int,
                 height: int,
                 border_buffer: float,
                 obstacle_buffer: float,
                 zones: list[BaseArenaZone],
                 chunk_size: int = 10,
                 grid_manager_logger: Logger = Logger(
                     identifier="GridManager",
                     decorator_level=LogLevels.INFO,
                     print_log_level=LogLevels.DEBUG,
                     file_log_level=LogLevels.DEBUG
                 )
                 ) -> None:
        self.logger: Logger = logger

        self.width: int = width
        self.height: int = height

        self.border_buffer: float = border_buffer
        self.obstacle_buffer: float = obstacle_buffer

        # Add buffer to all zones
        self.zones: list[BaseArenaZone] = []
        for zone in zones:
            zone.polygon = self.__add_buffer_to_zone(zone.polygon, self.obstacle_buffer)
            self.zones.append(zone)

        # Add border zone
        self.zones.append(self.__create_arena_border_zone())

        # Init grid manager
        self.grid_manager: GridManager = GridManager(
            grid_manager_logger, chunk_size, width, height
        )

        # Add all forbidden zones to the grid manager
        for zone in zones:
            # Only add any team forbidden zone and border zone to the grid manager
            if zone.zone_type in [ZoneType.FORBIDDEN, ZoneType.BORDER_ZONE]:
                self.grid_manager.add_forbidden_static_zone(zone.polygon)

    def __add_buffer_to_zone(self, zone: Polygon, buffer: float) -> Polygon:
        # TODO: cap_style does not work as expected
        return zone.buffer(buffer, cap_style=BufferCapStyle.square)  # square because of square chunk division

    def __create_arena_border_zone(self) -> BorderZone:
        """
        Create a border zone (contour) around the arena with a specific width.
        This prevents the robot from getting too close to the edges.
        """

        arena_polygon = box(0, 0, self.width, self.height)

        inner_polygon = self.__add_buffer_to_zone(arena_polygon, -self.border_buffer)

        self.__add_buffer_to_zone(inner_polygon, self.border_buffer)
        border_zone_polygon = arena_polygon.difference(inner_polygon)

        return BorderZone(polygon=border_zone_polygon)

    """ Viz """

    def visualize(self, show_buffer=True) -> None:
        """
        Visualize the arena, including its border and forbidden zones.
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw the arena
        arena_polygon = box(0, 0, self.width, self.height)
        self.__plot_polygon(ax, arena_polygon, color='lightgrey', label='Arena')

        for zone in self.zones:
            if show_buffer and zone.zone_type != ZoneType.BORDER_ZONE:
                # Plot the full buffer zone in light red
                buffer_polygon = self.__add_buffer_to_zone(zone.polygon, self.obstacle_buffer)
                self.__plot_polygon(ax, buffer_polygon, color='lightcoral', label=f"{zone.zone_type.name} Buffer")

            # Plot the original zone in dark red
            self.__plot_polygon(ax, zone.polygon, color='darkred', label=f"{zone.zone_type.name} Zone")

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title("Arena Visualization")
        ax.legend()
        plt.show()

    def __plot_polygon(self, ax, polygon: Polygon, color: str, label: str = None) -> None:
        """
        Helper method to plot a Polygon or MultiPolygon on the given axis.
        - Fill polygons without holes.
        - Only draw the outline (in dashed lines) for polygons with holes.
        """
        if len(polygon.interiors) == 0:
            # No holes: fill the polygon
            x, y = polygon.exterior.xy
            ax.fill(x, y, alpha=0.5, fc=color, label=label)
        else:
            # Polygon with holes: draw only the outline
            x, y = polygon.exterior.xy
            ax.plot(x, y, color=color, linestyle='--', label=label)  # Dashed outline
            # Draw outlines of interior holes
            for interior in polygon.interiors:
                x, y = interior.xy
                ax.plot(x, y, color=color, linestyle='--')  # Dashed lines for holes
