# External imports
import numpy as np
import asyncio
import math

# Import from common
from config_loader import CONFIG

from brain import Brain

from geometry import (
    OrientedPoint,
    Point,
    MultiPoint,
    is_empty,
    nearest_points,
    distance,
)
from WS_comms import WSmsg, WSclientRouteManager
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels
from utils import Utils

# Import from local path
from sensors import Lidar
from utils import LidarMode, AntiCollisionHandle


def get_ennemy_angle(self) -> float | None:
    if self.arena.ennemy_position is None:
        return None
    else:
        return (
            (
                math.atan2(
                    self.arena.ennemy_position.y - self.rolling_basis.odometrie.y,
                    self.arena.ennemy_position.x - self.rolling_basis.odometrie.x,
                )
            )
            - self.rolling_basis.odometrie.theta
        ) % math.tau


@Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
async def compute_ennemy_position(self):
    """
    Computes the position of the enemy based on lidar scans and updates the arena.

    This function calculates the position of the enemy by processing the lidar scans.
    It removes any obstacles that are outside the arena, and then determines the closest obstacle as the enemy position.
    It uses led to display the direction of the enemy.
    If the enemy position is within a pickup zone, it marks that zone as visited.

    Args:
        self: The instance of the class.

    Returns:
        None
    """
    polars: np.ndarray = self.lidar.scan_to_polars()
    obstacles: MultiPoint | Point = self.arena.remove_outside(
        self.pol_to_abs_cart(polars)
    )

    self.arena.ennemy_position = (
        None
        if is_empty(obstacles)
        else nearest_points(self.rolling_basis.odometrie, obstacles)[1]
    )

    trigger_acs = False

    if self.arena.ennemy_position is not None:
        if (
            distance(self.rolling_basis.odometrie, self.arena.ennemy_position)
            <= CONFIG.STOP_TRESHOLD
        ):

            angle = self.get_ennemy_angle()
            if angle > math.pi:
                angle = (-angle) % math.tau

            match self.anticollision_mode:

                case LidarMode.CIRCULAR:
                    trigger_acs = True

                case LidarMode.FRONTAL:
                    trigger_acs = abs(angle) < CONFIG.LIDAR_FRONTAL_DETECTION_ANGLE

                case LidarMode.SEMI_CIRCULAR:
                    trigger_acs = (
                        abs(angle) < CONFIG.LIDAR_SEMI_CIRCULAR_DETECTION_ANGLE
                    )
                case _:
                    raise Exception(
                        f"Unimplemented AnticollisionMode{self.anticollision_mode}"
                    )

    if trigger_acs:
        self.logger.log(
            "ACS triggered, performing emergency stop", LogLevels.WARNING, self.leds
        )
        self.handle_acs()  # Stop the robot. the go_to will abort and handle_acs triggered

    else:
        pass

    self.leds.set_lidar_info(
        trigger_acs,
        self.get_ennemy_angle(),
        (CONFIG.LIDAR_MAX_ANGLE - CONFIG.LIDAR_MIN_ANGLE) / 2,
        -(CONFIG.LIDAR_MAX_ANGLE - CONFIG.LIDAR_MIN_ANGLE) / 2,
    )

    for i in range(len(self.arena.pickup_zones)):
        if self.arena.pickup_zones[i].zone.contains(self.arena.ennemy_position):
            self.arena.pickup_zones[i].visit()
            self.logger.log(f"Ennemy visited pickup zone n°{i}", LogLevels.INFO)
            break


def pol_to_abs_cart(self, polars: np.ndarray) -> MultiPoint:
    """
    Converts polar coordinates to absolute Cartesian coordinates.

    Args:
        polars (np.ndarray): Array of polar coordinates in the form of (angle, distance).

    Returns:
        MultiPoint: Array of absolute Cartesian coordinates.
    """
    return MultiPoint(
        [
            (
                self.rolling_basis.odometrie.x
                + np.cos(self.rolling_basis.odometrie.theta + polars[i, 0])
                * polars[i, 1],
                self.rolling_basis.odometrie.y
                + np.sin(self.rolling_basis.odometrie.theta + polars[i, 0])
                * polars[i, 1],
            )
            for i in range(len(polars))
        ]
    )


@Brain.task(process=False, run_on_start=True, refresh_rate=2)
async def print_odometer(self):
    self.logger.log(
        f"Odometer: {Utils.geom_to_str(self.rolling_basis.odometrie)}",
        LogLevels.DEBUG,
    )
