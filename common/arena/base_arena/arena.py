# ====== Imports ======
# Standard library imports
from math import cos, sin, radians

# Third-party library imports
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
from shapely.geometry.base import BaseGeometry

# Internal project imports
from geometry import (
    Point,
    MultiPoint,
    Polygon as GeometryPolygon,
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
)
from logger import Logger, LogLevels
from arena.grid_manager import GridManager
from arena.arena_zone import (
    ZoneType,
    BaseArenaZone,
    EnemyZone,
    StuffZone,
    BlueReservedZone,
    YellowReservedZone,
    BorderZone,
    ZoneAccessibility,
)


# ====== Arena Class ======
class Arena:
    """
    Represents the arena and its zones, including buffer zones and borders.

    Attributes:
        logger (Logger): Logger instance for logging information.
        width (int): Width of the arena in centimeters.
        height (int): Height of the arena in centimeters.
        border_buffer (float): Buffer distance for the arena border.
        obstacle_buffer (float): Buffer distance for obstacles.
        zones (list[BaseArenaZone]): List of all zones in the arena.
        grid_manager (GridManager): Grid manager instance for managing zones.
    """

    def __init__(
        self,
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
            file_log_level=LogLevels.DEBUG,
        ),
    ) -> None:
        self.logger: Logger = logger

        self.width: int = width
        self.height: int = height

        self.border_buffer: float = border_buffer
        self.obstacle_buffer: float = obstacle_buffer

        # Initialize zones with added buffer
        self.zones: list[BaseArenaZone] = []
        for zone in zones:
            zone.polygon = self.__add_buffer_to_zone(zone.polygon, self.obstacle_buffer)
            self.zones.append(zone)

        # Add border zone
        self.zones.append(self.__create_arena_border_zone())

        # Initialize grid manager
        self.grid_manager: GridManager = GridManager(
            grid_manager_logger, chunk_size, width, height
        )

        # Add forbidden and border zones to the grid manager
        for zone in zones:
            if zone.accessibility == ZoneAccessibility.FORBIDDEN:
                self.grid_manager.add_forbidden_static_zone(zone.polygon)

    # ====== Private Methods ======

    def __add_buffer_to_zone(self, zone: Polygon, buffer: float) -> Polygon:
        """
        Adds a buffer around a zone to account for obstacle or border spacing.
        The buffer uses a square cap style to match the grid structure.
        """
        return zone.buffer(buffer, cap_style=BufferCapStyle.square)

    def __create_arena_border_zone(self) -> BorderZone:
        """
        Create a border zone around the arena with a specified buffer width.
        Prevents the robot from approaching too close to the arena edges.
        """
        arena_polygon = box(0, 0, self.width, self.height)
        inner_polygon = self.__add_buffer_to_zone(arena_polygon, -self.border_buffer)
        border_zone_polygon = arena_polygon.difference(inner_polygon)

        return BorderZone(polygon=border_zone_polygon)

    def __plot_polygon(
        self, ax, polygon: Polygon, color: str, label: str = None
    ) -> None:
        """
        Helper method to plot a polygon or multipolygon on a matplotlib axis.

        - Fills polygons without holes.
        - Draws only outlines (dashed) for polygons with holes.
        """
        if len(polygon.interiors) == 0:
            x, y = polygon.exterior.xy
            ax.fill(x, y, alpha=0.5, fc=color, label=label)
        else:
            x, y = polygon.exterior.xy
            ax.plot(x, y, color=color, linestyle="--", label=label)
            for interior in polygon.interiors:
                x, y = interior.xy
                ax.plot(x, y, color=color, linestyle="--")

    # ====== Public Methods ======

    def visualize(self, show_buffer: bool = True) -> None:
        """
        Visualize the arena, including its zones and optional buffer zones.

        Args:
            show_buffer (bool): If True, buffer zones are displayed.
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw the arena boundary
        arena_polygon = box(0, 0, self.width, self.height)
        self.__plot_polygon(ax, arena_polygon, color="lightgrey", label="Arena")
        seen_zone_types = set()
        first = True
        for zone in self.zones:
            if show_buffer and zone.zone_type != ZoneType.BORDER_ZONE:
                buffer_polygon = self.__add_buffer_to_zone(
                    zone.polygon, self.obstacle_buffer
                )
                self.__plot_polygon(
                    ax,
                    buffer_polygon,
                    color="#E89393",
                    label=f"zone Buffer" if first else None,
                )

                first = False
            self.__plot_polygon(
                ax,
                zone.polygon,
                color=zone.zone_color,
                label=(
                    f"{zone.zone_type.name} Zone"
                    if zone.zone_type.name not in seen_zone_types
                    else None
                ),
            )
            seen_zone_types.add(zone.zone_type.name)

            if zone.navigability == ZoneNavigability.FORBIDDEN:
                x, y = zone.polygon.exterior.xy
                ax.fill(
                    x, y, alpha=0.3, hatch="x", color=zone.zone_color, edgecolor="black"
                )

            elif zone.navigability == ZoneNavigability.RESTRICTED:
                x, y = zone.polygon.exterior.xy
                ax.fill(
                    x, y, alpha=0.3, hatch="/", color=zone.zone_color, edgecolor="black"
                )

        # Configure plot appearance
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Arena Visualization")
        ax.legend()
        plt.show()


# ====== Code Summary ======
# The Arena class models a physical arena with zones, border buffers, and obstacles.
# It initializes a list of zones with added buffers and includes a GridManager for managing grid-based zones.
# Methods include creating border zones, adding buffers to zones, and visualizing the arena with optional buffer zones.
