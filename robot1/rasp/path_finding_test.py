import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time

from matplotlib.animation import FuncAnimation
from config_loader import CONFIG
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

# Import from common
from WS_comms import WSclient, WSclientRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from geometry import OrientedPoint
from arena import MarsArena
from arena import Arena2, BaseArenaZone, ZoneType, EnemyZone, StuffZone, ForbiddenZone, BlueReservedZone, YellowReservedZone, BorderZone

from pathfinding.core.grid import Grid, GridNode

from path_finding import (
    PathFinder
)

arena_logger = Logger(
    identifier="NewArena",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG
)
finder_logger = Logger(
    identifier="PathFinder",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG
)


chunk_size = 10

arena = Arena2(
    logger=arena_logger,
    width=300,
    height=200,
    border_buffer=2,
    obstacle_buffer=5,
    zones=[
        ForbiddenZone(create_straight_rectangle(Point(45, 0), Point(0, 45))),
        ForbiddenZone(create_straight_rectangle(Point(77.5, 0), Point(122.5, 45))),
        ForbiddenZone(create_straight_rectangle(Point(155, 0), Point(200, 45))),
        ForbiddenZone(create_straight_rectangle(Point(45, 255), Point(0, 155))),
        ForbiddenZone(create_straight_rectangle(Point(77.5, 255), Point(122.5, 155))),
        ForbiddenZone(create_straight_rectangle(Point(155, 255), Point(200, 155))),
    ],
    chunk_size=chunk_size
)

arena_grid = arena.grid_manager.static_grid


finder = PathFinder(
    logger=finder_logger,
    start=OrientedPoint(10, 100, 0.0),
    goal=OrientedPoint(250, 150, 0.0),
    grid=arena_grid,
    chunk_size=chunk_size
)

path = finder.find_oriented_path()
print(path)

finder.visualize()
finder.visualize_with_scores()
