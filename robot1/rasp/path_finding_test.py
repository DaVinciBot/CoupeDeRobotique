import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time

from matplotlib.animation import FuncAnimation
from config_loader import CONFIG

# Import from common
from WS_comms import WSclient, WSclientRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from geometry import OrientedPoint
from arena import MarsArena

from pathfinding.core.grid import Grid, GridNode

from path_finding import (
    PathFinder
)

def generate_grid(width_cm, height_cm, chunk_size_cm, obstacle_ratio):
    """Génère une grille avec obstacles aléatoires."""
    width = width_cm // chunk_size_cm
    height = height_cm // chunk_size_cm
    grid = [[1 if random.random() > obstacle_ratio else 0 for _ in range(width)] for _ in range(height)]
    return grid

chunk_size = 10
grid = generate_grid(width_cm=300, height_cm=200, chunk_size_cm=chunk_size, obstacle_ratio=0.1)
start = (1, 1)
goal = (13, 8)
grid[start[1]][start[0]] = 1  # Assurez-vous que le point de départ est accessible
grid[goal[1]][goal[0]] = 1  # Assurez-vous que le point d'arrivée est accessible


finder_logger = Logger(
    identifier="PathFinder",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG
)

finder = PathFinder(
    logger=finder_logger,
    start=OrientedPoint(10, 20, 0.0),
    goal=OrientedPoint(200, 150, 0.0),
    grid=Grid(matrix=grid),
    chunk_size=chunk_size
)

path = finder.find_oriented_path()
print(path)

finder.visualize()