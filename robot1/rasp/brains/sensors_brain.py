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
from brains.acs import AntiCollisionMode, AntiCollisionHandle


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
    polars: np.ndarray = self.lidar.scan_to_polars()
    # self.logger.log(f"Polars ({polars.shape}): {polars.tolist()}", LogLevels.INFO)
    obstacles: MultiPoint | Point = self.arena.remove_outside(
        self.pol_to_abs_cart(polars)
    )

    # self.logger.log(f"obstacles: {obstacles}", LogLevels.DEBUG)

    # For now, the closest will be the enemy position
    self.arena.ennemy_position = (
        None
        if is_empty(obstacles)
        else nearest_points(self.rolling_basis.odometrie, obstacles)[1]
    )

    # self.logger.log(f"Ennemy position: {self.arena.ennemy_position}", LogLevels.INFO)

    self.logger.log(
        (
            f"Ennemy position computed: {Utils.geom_to_str(self.arena.ennemy_position) if self.arena.ennemy_position is not None else 'None'}"
            + (
                ""
                if self.arena.ennemy_position is None
                else f", at relative angle: {str(round(math.degrees(self.get_ennemy_angle())))} and distance: {round(distance(self.arena.ennemy_position,self.rolling_basis.odometrie))}"
            )
        ),
        LogLevels.DEBUG,
    )

    trigger_acs = False

    if self.arena.ennemy_position is not None:
        if (
            distance(self.rolling_basis.odometrie, self.arena.ennemy_position)
            <= CONFIG.STOP_TRESHOLD
        ):

            angle = self.get_ennemy_angle()
            if angle > math.pi:  # Tmp, ugly
                angle = (-angle) % math.tau

            match self.anticollision_mode:

                case AntiCollisionMode.DISABLED:
                    pass

                case AntiCollisionMode.CIRCULAR:
                    trigger_acs = True

                case AntiCollisionMode.FRONTAL:
                    trigger_acs = abs(angle) < CONFIG.LIDAR_FRONTAL_DETECTION_ANGLE

                case AntiCollisionMode.SEMI_CIRCULAR:
                    trigger_acs = (
                        abs(angle) < CONFIG.LIDAR_SEMI_CIRCULAR_DETECTION_ANGLE
                    )
                case _:
                    raise Exception(f"Unimplemented {self.anticollision_mode}")

    if trigger_acs:
        self.logger.log(
            "ACS triggered, performing emergency stop", LogLevels.WARNING, self.leds
        )
        self.rolling_basis.stop_and_clear_queue()
    else:
        # self.logger.log("ACS not triggered", LogLevels.DEBUG)
        pass

    self.leds.set_lidar_info(
        trigger_acs,
        self.get_ennemy_angle(),
        # Config values are centered to the right of the Lidar, but we have since switched to being centered on the front so we just balance out the extremums
        (CONFIG.LIDAR_MAX_ANGLE - CONFIG.LIDAR_MIN_ANGLE) / 2,
        -(CONFIG.LIDAR_MAX_ANGLE - CONFIG.LIDAR_MIN_ANGLE) / 2,
    )
    
    # mark the zone as visited if the ennemy is in it
    for i in range(self.arena.pickup_zones):
        if self.arena.pickup_zones[i].zone.contains(self.arena.ennemy_position):
            self.arena.pickup_zones[i].visit()
            self.logger.log(f"Ennemy visited pickup zone n°{i}", LogLevels.INFO)
            break


def pol_to_abs_cart(self, polars: np.ndarray) -> MultiPoint:
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
