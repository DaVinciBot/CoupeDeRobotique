# ====== Imports ======
# Standard library imports
import functools

# Third-party library imports
import matplotlib.pyplot as plt
from shapely.geometry import box
from pathfinding.core.grid import Grid, GridNode

# Internal project imports
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
)
from logger import Logger, LogLevels

# TODO - Handle Restricted Zones. Currently, only forbidden zones are handled. Restricted zones are zones where movement is restricted but not completely forbidden.
# First consider Restricted as obstacles but if no path is found, consider them as free zones.
# ====== GridManager Class ======
class GridManager:
    """
    Manages a grid for pathfinding and collision detection.
    Includes static and dynamic forbidden zones and grid visualization.
    """

    def __init__(
        self, logger: Logger, chunk_size: int, width: int, height: int
    ) -> None:
        """
        Initializes the grid manager.

        Args:
            logger (Logger): Logger instance for logging errors and information.
            chunk_size (int): Size of each grid chunk.
            width (int): Total width of the grid in absolute units.
            height (int): Total height of the grid in absolute units.
        """
        self.logger: Logger = logger

        # Validate chunk size against grid dimensions
        if width % chunk_size != 0 or height % chunk_size != 0:
            self.logger.log(
                f"[GRID] width and height must be multiples of chunk_size. "
                f"Chunk size will be adjusted to the nearest multiple.",
                LogLevels.ERROR,
            )
            chunk_size = min(width, height, key=lambda x: abs(x - chunk_size))

        self.chunk_size: int = chunk_size
        self.half_chunk_size: float = chunk_size / 2
        self.absolute_width: int = width
        self.absolute_height: int = height
        self.grid_width: int = width // chunk_size
        self.grid_height: int = height // chunk_size

        self.static_forbidden_zones: list[Polygon] = []
        self.dynamic_forbidden_zones: list[Polygon] = []

        # Grids for static and combined zones
        self.static_grid: Grid = self.__generate_base_grid()
        self.static_and_dynamic_grid: Grid = self.__generate_base_grid()

    # ====== Private Methods ======

    def __generate_base_grid(self) -> Grid:
        """Generates a base grid with all cells walkable."""
        return Grid(
            matrix=[
                [1 for _ in range(self.grid_width)] for _ in range(self.grid_height)
            ]
        )

    def __get_grid_node_center(self, node: GridNode) -> tuple[float, float]:
        """Calculates the absolute center coordinates of a grid node."""
        return (
            node.x * self.chunk_size + self.half_chunk_size,
            node.y * self.chunk_size + self.half_chunk_size,
        )

    @functools.lru_cache  # Avoid redundant calculations
    def __mark_zone_as_forbidden(self, grid: Grid, polygon_to_mark: Polygon) -> Grid:
        """
        Marks cells in the grid as forbidden based on intersection with a polygon.

        Args:
            grid (Grid): The grid to modify.
            polygon_to_mark (Polygon): The polygon defining forbidden zones.
        """
        minx, miny, maxx, maxy = polygon_to_mark.bounds
        min_row, max_row = int(miny // self.chunk_size), int(maxy // self.chunk_size)
        min_col, max_col = int(minx // self.chunk_size), int(maxx // self.chunk_size)

        for row in range(max(min_row, 0), min(max_row + 1, self.grid_height)):
            for col in range(max(min_col, 0), min(max_col + 1, self.grid_width)):
                cell = box(
                    col * self.chunk_size,
                    row * self.chunk_size,
                    (col + 1) * self.chunk_size,
                    (row + 1) * self.chunk_size,
                )
                if polygon_to_mark.intersects(cell):
                    grid.nodes[row][col].walkable = False
        return grid

    def __absolute_coords_to_grid_coords(
        self, point: OrientedPoint | Point
    ) -> GridNode:
        """Converts absolute coordinates to grid coordinates."""
        return GridNode(point.x / self.chunk_size, point.y / self.chunk_size)

    def __grid_coords_to_absolute_coords(self, node: GridNode) -> Point:
        """Converts grid coordinates to absolute coordinates."""
        x, y = self.__get_grid_node_center(node)
        return Point(x, y)

    def __update_grid(
        self, *, update_static_zones=False, update_dynamic_zones=False
    ) -> None:
        """
        Updates the grids for static and dynamic zones.

        Args:
            update_static_zones (bool): Whether to update static zones.
            update_dynamic_zones (bool): Whether to update dynamic zones.
        """
        if update_static_zones:
            for zone in self.static_forbidden_zones:
                self.static_grid = self.__mark_zone_as_forbidden(
                    grid=self.static_grid, polygon_to_mark=zone
                )
                self.static_and_dynamic_grid = self.__mark_zone_as_forbidden(
                    grid=self.static_grid, polygon_to_mark=zone
                )

        if update_dynamic_zones:
            for zone in self.dynamic_forbidden_zones:
                self.static_and_dynamic_grid = self.__mark_zone_as_forbidden(
                    grid=self.static_grid, polygon_to_mark=zone
                )

    # ====== Public Methods ======

    def add_forbidden_static_zone(
        self, forbidden_zones: Polygon | list[Polygon]
    ) -> None:
        """
        Adds static forbidden zones to the grid.

        Args:
            forbidden_zones (Polygon | list[Polygon]): Zones to mark as static forbidden areas.
        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.static_forbidden_zones.extend(forbidden_zones)
        self.__update_grid(update_static_zones=True)

    def remove_forbidden_static_zone(
        self, forbidden_zones_to_remove: Polygon | list[Polygon]
    ) -> None:
        """
        Removes static forbidden zones from the grid.

        Args:
            forbidden_zones_to_remove (Polygon | list[Polygon]): Zones to remove from static forbidden areas.
        """
        if not isinstance(forbidden_zones_to_remove, list):
            forbidden_zones_to_remove = [forbidden_zones_to_remove]

        self.static_forbidden_zones = [
            zone
            for zone in self.static_forbidden_zones
            if zone not in forbidden_zones_to_remove
        ]
        self.__update_grid(update_static_zones=True)

    def update_dynamic_forbidden_zones(self, forbidden_zones: list[Polygon]) -> None:
        """
        Updates dynamic forbidden zones in the grid.

        Args:
            forbidden_zones (list[Polygon]): Dynamic zones to add or update.
        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.dynamic_forbidden_zones = forbidden_zones
        self.__update_grid(update_dynamic_zones=True)

    def get_static_grid(self) -> Grid:
        """Returns the static grid."""
        return self.static_grid

    def get_static_and_dynamic_grid(self) -> Grid:
        """Returns the combined static and dynamic grid."""
        return self.static_and_dynamic_grid

    def visualize(self, only_static_grid: bool = False) -> None:
        """
        Visualizes the grid using matplotlib.

        Args:
            only_static_grid (bool): Whether to show only the static grid.
        """
        grid_to_visualize = (
            self.static_grid if only_static_grid else self.static_and_dynamic_grid
        )
        rows, cols = grid_to_visualize.height, grid_to_visualize.width

        fig, ax = plt.subplots(figsize=(10, 10))
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if not grid_to_visualize.node(x, y).walkable:
                    ax.add_patch(plt.Rectangle((x, rows - y - 1), 1, 1, color="black"))

        ax.set_xticks(range(cols))
        ax.set_yticks(range(rows))
        ax.grid(True)
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect("equal")
        ax.set_title("Arena Grid Visualization")
        plt.show()


# ====== Code Summary ======
# This implementation defines the GridManager class, which manages a grid for pathfinding and collision detection.
# Imports are organized into standard library, third-party, and internal project sections for clarity.
# Private methods handle grid generation, coordinate conversions, and marking forbidden zones, ensuring encapsulation.
# Public methods allow adding/removing static zones, updating dynamic zones, and retrieving or visualizing grids.
# The visualization method uses matplotlib for clear grid rendering, showing obstacles and walkable areas effectively.
