"""Grid management utilities for pathfinding and obstacle handling."""

import copy
from typing import Any, override

import matplotlib.pyplot as plt
import numpy as np
from loggerplusplus import Logger, LogLevels, time_tracker
from matplotlib.ticker import MaxNLocator
from pathfinding.core.grid import Grid, GridNode
from shapely.strtree import STRtree

from geometry import OrientedPoint, Point, Polygon, box


class GridManager:
    """Manages a grid for pathfinding and collision detection.
    Includes static and dynamic forbidden zones and grid visualization.

    - The grid uses a coordinate system where the origin is in the bottom-right corner.
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
        """Initializes the grid manager.

        Args:
            logger (Logger): Logger instance for logging errors and information.
            chunk_size (int): Size of each grid chunk.
            width (int): Total width of the grid in absolute units.
            height (int): Total height of the grid in absolute units.
            forbidden_cover_threshold (float, optional): Minimum coverage ratio
                for a cell to be marked as forbidden. Defaults to 0.5.

        """
        self.logger: Logger = logger
        self.forbidden_cover_threshold: float = forbidden_cover_threshold

        # Validate chunk size
        if width % chunk_size != 0 or height % chunk_size != 0:
            self.logger.log(
                "[GRID] width and height must be multiples of chunk_size. "
                "Chunk size will be adjusted to the nearest multiple.",
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
        """Generate a base grid with all cells walkable.

        Returns:
            Grid: Newly created walkable grid.

        """
        return Grid(
            matrix=[
                [1 for _ in range(self.grid_width)] for _ in range(self.grid_height)
            ],
        )

    @time_tracker(lambda self: self.logger)
    def __mark_zone(
        self,
        grid: Grid,
        polygon_to_mark: Polygon,
        *,
        walkable: bool,
    ) -> Grid:
        grid = copy.deepcopy(grid)
        minx, miny, maxx, maxy = polygon_to_mark.bounds

        min_col, max_col = (
            int((self.absolute_width - maxx) // self.chunk_size),
            int((self.absolute_width - minx) // self.chunk_size),
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
                            polygon.intersects(cell)
                            for polygon in self.static_forbidden_zones
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
    def __optimized_mark_zone(  # QUESTION: Useless ?
        self,
        grid: Grid,
        polygon_to_mark: Polygon,
        *,
        walkable: bool,
    ) -> Grid:
        """Marks cells in the grid as forbidden based on intersection with a polygon.

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
            0,
            int((self.grid_width * self.chunk_size - maxx) // self.chunk_size),
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

    @time_tracker(lambda self: self.logger)
    def __update_grid(
        self,
        *,
        update_static_zones: bool = False,
        update_dynamic_zones: bool = False,
        clear_grid: bool = False,
    ) -> None:
        """Update the grids for static and dynamic zones.

        Args:
            update_static_zones (bool, optional):
                Whether to update static zones. Defaults to ``False``.
            update_dynamic_zones (bool, optional):
                Whether to update dynamic zones. Defaults to ``False``.
            clear_grid (bool, optional):
                If ``True``, regenerate empty grids before updating.
                Defaults to ``False``.

        """
        if clear_grid:
            self.static_grid = self.__generate_base_grid()
            self.static_and_dynamic_grid = self.__generate_base_grid()

        # 1. Update all not updated forbidden zones, based on the update flags
        # 1.1 Update static zones
        if update_static_zones:
            for zone_to_update in self.not_updated_forbidden_zones:
                # 1.1.1 Update static grid
                self.static_grid = self.__mark_zone(
                    grid=self.static_grid,
                    polygon_to_mark=zone_to_update,
                    walkable=zone_to_update not in self.static_forbidden_zones,
                )
                # 1.1.2 Also update the static_and_dynamic grid (only static part of the grid)
                self.static_and_dynamic_grid = self.__mark_zone(
                    grid=self.static_and_dynamic_grid,
                    polygon_to_mark=zone_to_update,
                    walkable=zone_to_update not in self.static_forbidden_zones,
                )

        # 1.2 Update dynamic zones
        if update_dynamic_zones:
            # 1.2.1 Clear all dynamic zones (get deep copy of static grid)
            self.static_and_dynamic_grid = copy.deepcopy(self.static_grid)

            # 1.2.2 Then mark the new dynamic zone as forbidden
            for zone_to_update in self.not_updated_forbidden_zones:
                self.static_and_dynamic_grid = self.__mark_zone(
                    grid=self.static_and_dynamic_grid,
                    polygon_to_mark=zone_to_update,
                    walkable=False,  # Dynamic zone are always forbidden
                )

        self.not_updated_forbidden_zones: list[Polygon] = []

    # ====== Public Methods ======
    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GridManager):
            return False

        def grid_to_numpy(grid: Grid) -> np.ndarray[Any, np.dtype[np.bool_]]:
            return np.array(
                [[1 if node.walkable else 0 for node in row] for row in grid.nodes],
                dtype=bool,
            )

        return (
            self.chunk_size == other.chunk_size
            and self.absolute_width == other.absolute_width
            and self.absolute_height == other.absolute_height
            and self.grid_width == other.grid_width
            and self.grid_height == other.grid_height
            and self.forbidden_cover_threshold == other.forbidden_cover_threshold
            and self.static_forbidden_zones == other.static_forbidden_zones
            and self.not_updated_forbidden_zones == other.not_updated_forbidden_zones
            and np.array_equal(
                grid_to_numpy(self.static_grid),
                grid_to_numpy(other.static_grid),
            )
            and np.array_equal(
                grid_to_numpy(self.static_and_dynamic_grid),
                grid_to_numpy(other.static_and_dynamic_grid),
            )
        )

    @override
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @override
    def __hash__(self) -> int:
        """Return a hash based on grid dimensions and chunk size."""
        return hash(
            (
                self.chunk_size,
                self.absolute_width,
                self.absolute_height,
                self.grid_width,
                self.grid_height,
            ),
        )

    @time_tracker(lambda self: self.logger)
    def add_forbidden_static_zone(
        self,
        forbidden_zones: Polygon | list[Polygon],
    ) -> None:
        """Add static forbidden zones to the grid.

        Args:
            forbidden_zones (Polygon | list[Polygon]):
                Zones to mark as static forbidden areas.

        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.static_forbidden_zones.extend(forbidden_zones)
        self.not_updated_forbidden_zones.extend(forbidden_zones)
        self.__update_grid(update_static_zones=True)

    @time_tracker(lambda self: self.logger)
    def remove_forbidden_static_zone(
        self,
        forbidden_zones_to_remove: Polygon | list[Polygon],
    ) -> None:
        """Remove static forbidden zones from the grid.

        Args:
            forbidden_zones_to_remove (Polygon | list[Polygon]):
                Zones to remove from static forbidden areas.

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
            self.static_forbidden_zones,
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
        """Updates dynamic forbidden zones in the grid.

        Args:
            forbidden_zones (list[Polygon]): Dynamic zones to add or update.

        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.not_updated_forbidden_zones.extend(forbidden_zones)
        self.__update_grid(update_dynamic_zones=True)

    def get_grid_node_center(self, node: GridNode) -> tuple[float, float]:
        """Calculate the absolute center coordinates of a grid node.

        Args:
            node (GridNode): Node within the grid.

        Returns:
            tuple[float, float]: ``(x, y)`` coordinates of the node center.

        """
        return (
            node.x * self.chunk_size + self.half_chunk_size,
            node.y * self.chunk_size + self.half_chunk_size,
        )

    def absolute_coords_to_grid_coords(self, point: OrientedPoint | Point) -> GridNode:
        """Convert absolute coordinates to grid coordinates.

        Args:
            point (OrientedPoint | Point): Absolute point to convert.

        Returns:
            GridNode: Corresponding node in the grid.

        """
        return GridNode(int(point.x / self.chunk_size), int(point.y / self.chunk_size))

    def grid_coords_to_absolute_coords(self, node: GridNode) -> Point:
        """Convert grid coordinates to absolute coordinates.

        Args:
            node (GridNode): Grid node to convert.

        Returns:
            Point: Absolute center point of the node.

        """
        x, y = self.get_grid_node_center(node)
        return Point(x, y)

    def get_static_grid(self) -> Grid:
        """Return the static grid used for pathfinding.

        Returns:
            Grid: Grid containing only static obstacles.

        """
        return self.static_grid

    def get_static_and_dynamic_grid(self) -> Grid:
        """Return the grid with both static and dynamic obstacles.

        Returns:
            Grid: Combined grid.

        """
        return self.static_and_dynamic_grid

    def visualize(
        self,
        *,
        only_static_grid: bool = False,
        path: list | None = None,
        show: bool = True,
        plot: tuple[plt.Axes, plt.Figure] | None = None,
    ) -> tuple[plt.Axes, plt.Figure]:
        """Visualize the grid using matplotlib.

        Args:
            only_static_grid (bool, optional):
                Whether to show only the static grid. Defaults to ``False``.
            path (list | None, optional):
                Path to draw on the grid, if provided. Defaults to None.
            show (bool, optional):
                Whether to display the plot. Defaults to ``True``.
            plot (tuple[plt.Axes, plt.Figure] | None, optional):
                Existing plot to reuse. Defaults to None.

        Returns:
            tuple[plt.Axes, plt.Figure]: Axis and figure of the plot.

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

        if path:
            for i in range(len(path) - 1):
                # Draw a line connecting the current node to the next node
                ax.plot(
                    [path[i].x, path[i + 1].x],
                    [path[i].y, path[i + 1].y],
                    color="purple",
                    linewidth=1,
                    alpha=0.2,
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

        ax.grid(visible=True)
        plt.tight_layout()
        if show:
            plt.show()

        return ax, fig
