# ====== Code Summary ======
# This implementation defines the GridManager class, which manages a grid for pathfinding and collision detection.
# Imports are organized into standard library, third-party, and internal project sections for clarity.
# Private methods handle grid generation, coordinate conversions, and marking forbidden zones, ensuring encapsulation.
# Public methods allow adding/removing static zones, updating dynamic zones, converting coordinates, and retrieving or
# visualizing grids.
# The visualization method uses matplotlib for clear grid rendering, showing obstacles and walkable areas effectively.

# ====== Imports ======
# Standard library imports
import functools
import copy

# Third-party library imports
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
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

# TODO: a explorer pour optimiser les recherches de zones interdites
from shapely.strtree import STRtree

from logger import Logger, LogLevels, time_tracker


# ====== GridManager Class ======
class GridManager:
    """
    Manages a grid for pathfinding and collision detection.
    Includes static and dynamic forbidden zones and grid visualization.

    Notes:
    - The grid uses a coordinate system where the origin is at the bottom-right corner.
    - X-axis increases towards the left, while Y-axis increases upwards.
    - This reference frame affects calculations and visualization; adjustments ensure alignment.
    """

    def __init__(
        self,
        logger: Logger,
        chunk_size: int,
        width: int,
        height: int,
        forbidden_cover_threshold: float = 0.5,
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
        self.forbidden_cover_threshold: float = forbidden_cover_threshold

        # Validate chunk size
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

        self.not_updated_forbidden_zones: list[Polygon] = []

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

    @time_tracker(lambda self: self.logger)
    def __mark_zone(self, grid: Grid, polygon_to_mark: Polygon, walkable: bool) -> Grid:
        grid = copy.deepcopy(grid)
        minx, miny, maxx, maxy = polygon_to_mark.bounds

        min_col, max_col = int((self.absolute_width - maxx) // self.chunk_size), int(
            (self.absolute_width - minx) // self.chunk_size
        )
        min_row, max_row = int(miny // self.chunk_size), int(maxy // self.chunk_size)

        for row in range(max(min_row, 0), min(max_row + 1, self.grid_height)):
            for col in range(max(min_col, 0), min(max_col + 1, self.grid_width)):
                actual_col = self.grid_width - 1 - col
                cell = box(
                    (self.grid_width - 1 - col) * self.chunk_size,
                    row * self.chunk_size,
                    (self.grid_width - col) * self.chunk_size,
                    (row + 1) * self.chunk_size,
                )

                if polygon_to_mark.intersects(cell):
                    if walkable:
                        if any(
                            [
                                polygon.intersects(cell)
                                for polygon in self.static_forbidden_zones
                            ]
                        ):
                            continue

                        grid.nodes[row][actual_col].walkable = walkable

                    if (
                        not walkable
                        and polygon_to_mark.intersection(cell).area / cell.area
                        >= self.forbidden_cover_threshold
                    ):
                        grid.nodes[row][actual_col].walkable = walkable

        return grid

    @time_tracker(lambda self: self.logger)
    def __optimized_mark_zone(
        self, grid: Grid, polygon_to_mark: Polygon, walkable: bool
    ) -> Grid:
        """
        Marks cells in the grid as forbidden based on intersection with a polygon.

        Args:
            grid (Grid): The grid to modify.
            polygon_to_mark (Polygon): The polygon defining forbidden zones.
            walkable (bool): Whether the cells should be marked as walkable.

        Returns:
            Grid: Updated grid with forbidden zones marked.
        """
        # Precompute polygon bounds and indices
        minx, miny, maxx, maxy = polygon_to_mark.bounds

        min_col = max(
            0, int((self.grid_width * self.chunk_size - maxx) // self.chunk_size)
        )
        max_col = min(
            self.grid_width,
            int((self.grid_width * self.chunk_size - minx) // self.chunk_size) + 1,
        )
        min_row = max(0, int(miny // self.chunk_size))
        max_row = min(self.grid_height, int(maxy // self.chunk_size) + 1)

        # Build STRtree with geometries
        if walkable and self.static_forbidden_zones:
            static_zone_tree = STRtree(self.static_forbidden_zones)

        # Iterate over relevant grid cells
        for row in range(min_row, max_row):
            for col in range(min_col, max_col):
                actual_col = self.grid_width - 1 - col
                cell = box(
                    actual_col * self.chunk_size,
                    row * self.chunk_size,
                    (actual_col + 1) * self.chunk_size,
                    (row + 1) * self.chunk_size,
                )

                # Check if the polygon intersects the grid cell
                if polygon_to_mark.intersects(cell):
                    # Check static forbidden zones if walkable
                    if walkable and self.static_forbidden_zones:
                        overlapping_zones = static_zone_tree.query(cell)
                        # Cast the ndarray to a list of Polygons
                        overlapping_polygons = [
                            self.static_forbidden_zones[i] for i in overlapping_zones
                        ]
                        if any(zone.intersects(cell) for zone in overlapping_polygons):
                            continue

                    # Update cell walkable status
                    grid.nodes[row][actual_col].walkable = walkable

        return grid

    def __update_grid(
        self, *, update_static_zones=False, update_dynamic_zones=False, clear_grid=False
    ) -> None:
        """
        Updates the grids for static and dynamic zones.

        Args:
            update_static_zones (bool): Whether to update static zones.
            update_dynamic_zones (bool): Whether to update dynamic zones.
        """
        if clear_grid:
            self.static_grid = self.__generate_base_grid()
            self.static_and_dynamic_grid = self.__generate_base_grid()

        if update_static_zones:
            for zone in self.not_updated_forbidden_zones:
                self.static_grid = self.__mark_zone(
                    grid=self.static_grid,
                    polygon_to_mark=zone,
                    walkable=zone not in self.static_forbidden_zones,
                )

        if update_dynamic_zones:
            for i in range(len(self.not_updated_forbidden_zones)):
                self.static_and_dynamic_grid = self.__mark_zone(
                    grid=self.static_grid if i == 0 else self.static_and_dynamic_grid,
                    polygon_to_mark=self.not_updated_forbidden_zones[i],
                    walkable=False,  # Dynamic zone are always forbidden
                )

        self.not_updated_forbidden_zones: list[Polygon] = []

    # ====== Public Methods ======
    @time_tracker(lambda self: self.logger)
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
        self.not_updated_forbidden_zones.extend(forbidden_zones)
        self.__update_grid(update_static_zones=True)

    @time_tracker(lambda self: self.logger)
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

        original_static_forbidden_zones = self.static_forbidden_zones[:]
        self.static_forbidden_zones = [
            zone
            for zone in self.static_forbidden_zones
            if zone not in forbidden_zones_to_remove
        ]

        removed_zones = set(original_static_forbidden_zones) - set(
            self.static_forbidden_zones
        )
        if not removed_zones:
            self.logger.log(
                "Call remove zone but no zone removed. Check if you use buffer.",
                LogLevels.WARNING,
            )

        self.not_updated_forbidden_zones.extend(forbidden_zones_to_remove)
        self.__update_grid(update_static_zones=True)

    @time_tracker(lambda self: self.logger)
    def update_dynamic_forbidden_zones(self, forbidden_zones: list[Polygon]) -> None:
        """
        Updates dynamic forbidden zones in the grid.

        Args:
            forbidden_zones (list[Polygon]): Dynamic zones to add or update.
        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.not_updated_forbidden_zones.extend(forbidden_zones)
        self.__update_grid(update_dynamic_zones=True)

    def get_grid_node_center(self, node: GridNode) -> tuple[float, float]:
        """Calculates the absolute center coordinates of a grid node."""
        return (
            node.x * self.chunk_size + self.half_chunk_size,
            node.y * self.chunk_size + self.half_chunk_size,
        )

    def absolute_coords_to_grid_coords(self, point: OrientedPoint | Point) -> GridNode:
        """Converts absolute coordinates to grid coordinates."""
        return GridNode(int(point.x / self.chunk_size), int(point.y / self.chunk_size))

    def grid_coords_to_absolute_coords(self, node: GridNode) -> Point:
        """Converts grid coordinates to absolute coordinates."""
        x, y = self.get_grid_node_center(node)
        return Point(x, y)

    def get_static_grid(self) -> Grid:
        """Returns the static grid."""
        return self.static_grid

    def get_static_and_dynamic_grid(self) -> Grid:
        """Returns the combined static and dynamic grid."""
        return self.static_and_dynamic_grid

    def visualize(
        self,
        only_static_grid: bool = False,
        path=None,
        show: bool = True,
        plot: tuple[plt.axes, plt.figure] = None,
    ) -> tuple[plt.axes, plt.figure]:
        """
        Visualizes the grid using matplotlib.

        Args:
            only_static_grid (bool): Whether to show only the static grid.
            path (list): List of coordinates representing a path (optional).
            show (bool): Whether to display the plot.
            plot (tuple[plt.axes, plt.figure]): Existing plot to use for visualization.
        """
        grid_to_visualize = (
            self.static_grid if only_static_grid else self.static_and_dynamic_grid
        )

        if plot:
            ax, fig = plot
        else:
            fig, ax = plt.subplots(figsize=(12, 6))

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if not grid_to_visualize.node(x, y).walkable:
                    ax.add_patch(plt.Rectangle((x, y), 1, 1, color="black"))

        if not isinstance(path, list):
            if path is None:
                path = []
            else:
                path = [path]

        for p in path:
            if p and len(p) > 1:
                for i in range(len(p) - 1):
                    # Draw a line connecting the current node to the next node
                    ax.plot(
                        [p[i].x / self.chunk_size, p[i + 1].x / self.chunk_size],
                        [p[i].y / self.chunk_size, p[i + 1].y / self.chunk_size],
                        color="green",
                        linewidth=2,
                    )

        ax.set_xticks(range(self.grid_width))
        ax.set_yticks(range(self.grid_height))

        ax.set_xlim(self.grid_width, 0)
        ax.set_ylim(0, self.grid_height)

        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=25))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=25))
        plt.xticks(rotation=45)

        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Arena Grid Visualization")

        ax.grid(True)
        plt.tight_layout()
        if show:
            plt.show()

        return ax, fig
