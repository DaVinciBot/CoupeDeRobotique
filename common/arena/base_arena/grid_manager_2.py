"""Legacy grid manager used for experimental pathfinding."""

from __future__ import annotations

import copy

import matplotlib.pyplot as plt
from old_logger import Logger, LogLevels, time_tracker
from pathfinding.core.grid import Grid, GridNode
from shapely.geometry import box
from shapely.strtree import STRtree

from geometry import OrientedPoint, Point, Polygon


class GridManager:
    """Manage a grid for pathfinding and collision detection.

    The manager builds static and dynamic grids to comply with the pathfinding
    library requirements and uses a spatial index for fast zone lookups.

    """

    def __init__(
        self,
        logger: Logger,
        chunk_size: int,
        width: int,
        height: int,
    ) -> None:
        """Initialize the grid manager.

        Args:
            logger (Logger): Logger used for debug information.
            chunk_size (int): Size of a grid cell in world units.
            width (int): Total width of the arena in world units.
            height (int): Total height of the arena in world units.

        """
        self.logger = logger
        self.chunk_size = chunk_size
        self.half_chunk_size = chunk_size / 2
        self.absolute_width = width
        self.absolute_height = height
        self.grid_width = width // chunk_size
        self.grid_height = height // chunk_size

        if width % chunk_size != 0 or height % chunk_size != 0:
            self.logger.log(
                (
                    "[GRID] width and height must be multiples of chunk_size. "
                    "Adjusting chunk size."
                ),
                LogLevels.WARNING,
            )
            chunk_size = min(width, height, key=lambda x: abs(x - chunk_size))

        self.static_grid = self.__generate_base_grid()
        self.dynamic_grid = self.__generate_base_grid()
        self.static_forbidden_zones = []
        self.dynamic_forbidden_zones = []
        self.spatial_index = STRtree([])

    # ====== Private Methods ======

    def __generate_base_grid(self) -> Grid:
        """Generate a base grid with all cells walkable.

        Returns:
            Grid: A grid where every node is initially walkable.

        """
        return Grid(
            matrix=[
                [1 for _ in range(self.grid_width)] for _ in range(self.grid_height)
            ],
        )

    def __update_spatial_index(self) -> None:
        """Updates the spatial index for static forbidden zones."""
        self.spatial_index = STRtree(self.static_forbidden_zones)

    def __mark_zone(
        self,
        grid: Grid,
        zones: list[Polygon],
        *,
        walkable: bool,
    ) -> Grid:
        """Marks cells in the grid as walkable or non-walkable based on zones.

        Args:
            grid (Grid): The grid to update.
            zones (list[Polygon]): The zones to mark.
            walkable (bool): Whether to mark the cells as walkable or not.

        Returns:
            Grid: Updated grid.

        """
        for polygon in zones:
            minx, miny, maxx, maxy = polygon.bounds

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

            for row in range(min_row, max_row):
                for col in range(min_col, max_col):
                    actual_col = self.grid_width - 1 - col
                    cell = box(
                        actual_col * self.chunk_size,
                        row * self.chunk_size,
                        (actual_col + 1) * self.chunk_size,
                        (row + 1) * self.chunk_size,
                    )

                    if polygon.intersects(cell):
                        if walkable and any(
                            zone.intersects(cell)
                            for zone in self.spatial_index.query(cell)
                        ):
                            continue
                        grid.nodes[row][actual_col].walkable = walkable

        return grid

    # ====== Public Methods ======

    @time_tracker(lambda self: self.logger)
    def add_forbidden_static_zone(
        self,
        forbidden_zones: Polygon | list[Polygon],
    ) -> None:
        """Add one or several static forbidden zones.

        Args:
            forbidden_zones (Polygon | list[Polygon]): Zone polygons that should
                be marked as non-walkable permanently.

        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.static_forbidden_zones.extend(forbidden_zones)
        self.__update_spatial_index()
        self.static_grid = self.__mark_zone(
            self.static_grid,
            forbidden_zones,
            walkable=False,
        )

    @time_tracker(lambda self: self.logger)
    def remove_forbidden_static_zone(
        self,
        forbidden_zones: Polygon | list[Polygon],
    ) -> None:
        """Remove static forbidden zones previously added.

        Args:
            forbidden_zones (Polygon | list[Polygon]): Polygons to remove from
                the set of static forbidden zones.

        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.static_forbidden_zones = [
            zone for zone in self.static_forbidden_zones if zone not in forbidden_zones
        ]
        self.__update_spatial_index()
        self.static_grid = self.__generate_base_grid()
        self.static_grid = self.__mark_zone(
            self.static_grid,
            self.static_forbidden_zones,
            walkable=False,
        )

    @time_tracker(lambda self: self.logger)
    def update_dynamic_forbidden_zones(self, dynamic_zones: list[Polygon]) -> None:
        """Update the list of dynamic forbidden zones.

        Args:
            dynamic_zones (list[Polygon]): Zones that can change during runtime
                and should be marked as non-walkable.

        """
        self.dynamic_forbidden_zones = dynamic_zones
        self.dynamic_grid = self.__mark_zone(
            copy.deepcopy(self.static_grid),
            dynamic_zones,
            walkable=False,
        )

    def get_grid_node_center(self, node: GridNode) -> tuple[float, float]:
        """Return the center coordinates of a grid node.

        Args:
            node (GridNode): The node to convert.

        Returns:
            tuple[float, float]: Coordinates of the node center in world units.

        """
        return (
            node.x * self.chunk_size + self.half_chunk_size,
            node.y * self.chunk_size + self.half_chunk_size,
        )

    def absolute_coords_to_grid_coords(self, point: OrientedPoint | Point) -> GridNode:
        """Convert absolute coordinates to grid coordinates.

        Args:
            point (OrientedPoint | Point): Point in world coordinates.

        Returns:
            GridNode: Corresponding node in the grid.

        """
        return GridNode(int(point.x / self.chunk_size), int(point.y / self.chunk_size))

    def grid_coords_to_absolute_coords(self, node: GridNode) -> Point:
        """Convert grid coordinates to absolute coordinates.

        Args:
            node (GridNode): Grid node to convert.

        Returns:
            Point: Center of the node in world coordinates.

        """
        x, y = self.get_grid_node_center(node)
        return Point(x, y)

    def get_static_grid(self) -> Grid:
        """Return the static grid used for pathfinding.

        Returns:
            Grid: The grid containing only static forbidden zones.

        """
        return self.static_grid

    def get_dynamic_grid(self) -> Grid:
        """Return the grid combining static and dynamic forbidden zones.

        Returns:
            Grid: The grid including both static and dynamic updates.

        """
        return self.dynamic_grid

    def visualize(
        self,
        *,
        only_static_grid: bool = False,
        path: list[GridNode] | None = None,
    ) -> None:
        """Visualize the grid using matplotlib.

        Args:
            only_static_grid (bool, optional):
                If ``True`` show only static zones. Defaults to ``False``.
            path (list[GridNode] | None, optional):
                Path to draw over the grid. Defaults to ``None``.

        """
        grid_to_visualize = self.static_grid if only_static_grid else self.dynamic_grid

        _fig, ax = plt.subplots(figsize=(12, 6))

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if not grid_to_visualize.node(x, y).walkable:
                    ax.add_patch(plt.Rectangle((x, y), 1, 1, color="black"))

        if path:
            for i in range(len(path) - 1):
                ax.plot(
                    [path[i].x, path[i + 1].x],
                    [path[i].y, path[i + 1].y],
                    color="green",
                    linewidth=2,
                )

        ax.set_xticks(range(self.grid_width))
        ax.set_yticks(range(self.grid_height))

        ax.set_xlim(0, self.grid_width)
        ax.set_ylim(0, self.grid_height)

        ax.grid(visible=True)
        plt.show()
