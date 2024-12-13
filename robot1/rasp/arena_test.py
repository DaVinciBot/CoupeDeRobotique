from config_loader import CONFIG

from pathfinding.core.grid import Grid, GridNode

from path_finding import PathFinder

from arena import (
    ShowArena,
    BaseArenaZone,
    BaseArena,
    ForbiddenZone,
    ZoneType,
    EnemyZone,
    StuffZone,
    BlueReservedZone,
    YellowReservedZone,
    BorderZone,
    ZoneAccessibility,
)

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
    box,
)
from logger import Logger, LogLevels


arena_logger = Logger(
    identifier="NewArena",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG,
)

arena = ShowArena(
    logger=arena_logger,
    border_buffer=10,
    obstacle_buffer=5,
    chunk_size=2,
)

arena.visualize()
arena.grid_manager.visualize()
