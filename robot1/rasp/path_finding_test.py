import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time

from matplotlib.animation import FuncAnimation
from config_loader import CONFIG

# Import from common
from WS_comms import WSclient, WSclientRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels,LogerAnalyser
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

def save_grid(grid, filename):
    """Sauvegarde la grille dans un fichier."""
    with open(filename, 'w') as f:
        for row in grid:
            f.write(' '.join(map(str, row)) + '\n')
            
def generate_config_grid(width_cm, height_cm, chunk_size, obstacle_size_cm=30):
    width = width_cm // chunk_size
    height = height_cm // chunk_size
    print(width,height)
    grid = [[1 for _ in range(width)] for _ in range(height)]
    obstacle_size = obstacle_size_cm // chunk_size
    
    i=random.randint(obstacle_size, height - obstacle_size)
    for row in range(i, i + obstacle_size):
        for col in range(width//2-obstacle_size//2,width//2+obstacle_size//2):
            grid[row][col] = 0
        
    return grid

def generate_grid_from_file(grid_path):
    with open(grid_path, 'r') as f:
        grid = [[int(cell) for cell in row.split()] for row in f]
    return grid

def test_path_finder():
    chunk_size = 2
    grid = generate_grid(width_cm=300, height_cm=200, chunk_size_cm=chunk_size, obstacle_ratio=0.3)
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
    start=OrientedPoint(10.8, 20, 0.0),
    goal=OrientedPoint(200, 150, 0.0),
    grid=Grid(matrix=grid),
    chunk_size=chunk_size
    )

    path = finder.find_oriented_path()
    print(path)

    finder.visualize()
    finder.visualize_with_scores()
    
def test_path_finder_match_config(width_cm=300, height_cm=200, chunk_size=2, obstacle_size_cm=30):
    finder_logger = Logger(
    identifier="PathFinder",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG
    )
    
    for i in range(200):
        grid = generate_config_grid(width_cm=width_cm, height_cm=height_cm, chunk_size=chunk_size, obstacle_size_cm=obstacle_size_cm)
        
        finder = PathFinder(
            logger=finder_logger,
            start=OrientedPoint(width_cm//2, 0, 0.0),
            goal=OrientedPoint(width_cm//2, height_cm-1, 0.0),
            grid=Grid(matrix=grid),
            chunk_size=chunk_size
        )
        finder.find_oriented_path()


# logger_analyser = LogerAnalyser("logs/2024-12-06.log")
# logger_analyser.analyse_func_time_tracker("find_oriented_path")

test_path_finder()