import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time
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
    box,
)


from matplotlib.animation import FuncAnimation
from config_loader import CONFIG

# Import from common
from WS_comms import WSclient, WSclientRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from geometry import OrientedPoint
from arena import (
    Arena,
    BaseArenaZone,
    ZoneType,
    EnemyZone,
    StuffZone,
    BlueReservedZone,
    YellowReservedZone,
    BorderZone,
    ZoneNavigability
)

from pathfinding.core.grid import Grid, GridNode

from path_finding import PathFinder


arena_logger = Logger(
    identifier="NewArena",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG,
)

arena = Arena(
    logger=arena_logger,
    width=300,
    height=200,
    border_buffer=2,
    obstacle_buffer=5,
    zones=[
        BaseArenaZone(create_straight_rectangle(Point(45, 0), Point(0, 45)),navigability=ZoneNavigability.FORBIDDEN),
        BaseArenaZone(create_straight_rectangle(Point(77.5, 0), Point(122.5, 45)),navigability=ZoneNavigability.FORBIDDEN),
        BaseArenaZone(create_straight_rectangle(Point(155, 0), Point(200, 45))),
        BaseArenaZone(create_straight_rectangle(Point(45, 255), Point(0, 155)),navigability=ZoneNavigability.RESTRICTED),
        BaseArenaZone(create_straight_rectangle(Point(77.5, 255), Point(122.5, 155))),
        BaseArenaZone(create_straight_rectangle(Point(155, 255), Point(200, 155))),
        StuffZone(create_straight_rectangle(Point(50, 50), Point(100, 100)),navigability=ZoneNavigability.FORBIDDEN),
        YellowReservedZone(create_straight_rectangle(Point(150, 50), Point(200, 100))),
        BlueReservedZone(create_straight_rectangle(Point(50, 150), Point(100, 200))),
        EnemyZone(create_straight_rectangle(Point(100, 100), Point(150, 150))),
        EnemyZone(create_straight_rectangle(Point(10, 10), Point(50, 50))),
    ],
    chunk_size=2,
)

arena.grid_manager.visualize()
arena.visualize()
