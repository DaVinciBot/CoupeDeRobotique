# External imports
import asyncio
import time
import math
from dataclasses import dataclass

# Import from common
from config_loader import CONFIG
from brain import Brain

from WS_comms import WSmsg, WSclientRouteManager, WServerRouteManager
from geometry import OrientedPoint, Point, distance, Polygon
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels
from led_strip import LEDStrip
from utils import Utils
from GPIO import PIN

# Import from local path
from controllers import RollingBasis


from path_finding import (
    PathFinder
)
from arena import Arena2

from deplacement_supervisor import MovementSupervisor

class MainBrain(Brain):

    def __init__(
        self,
        logger: Logger,
        rolling_basis: RollingBasis
    ) -> None:

        self.rolling_basis: RollingBasis

        """
                Get the state of the rolling basis
                """
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

        chunk_size = 5

        arena = Arena2(
            logger=arena_logger,
            width=300,
            height=200,
            border_buffer=2,
            obstacle_buffer=5,
            zones=[],
            chunk_size=chunk_size
        )

        arena_grid = arena.grid_manager.static_grid

        finder = PathFinder(
            logger=finder_logger,
            start=OrientedPoint(0, 0, 0.0),
            goal=OrientedPoint(0, 50, 0.0),
            grid=arena_grid,
            chunk_size=chunk_size
        )

        path = finder.find_oriented_path()

        CONFIG = {
            "SPEED_PROFILES": {
                "test_speed": {
                    "max_linear_speed": 50.0,  # Max 10.0 cm/s
                    "max_angular_speed": 3.0,  # Max 6.0 rad/s
                    "max_linear_acceleration": 0.5,  # Max 0.5 cm/s^2
                    "max_angular_acceleration": 0.1,  # Max 1.0 rad/s^2
                    "max_linear_deceleration": 0.4,  # Max 0.5 cm/s^2
                    "max_angular_deceleration": 0.1  # Max 1.0 rad/s^2
                }
            }
        }

        supervisor = MovementSupervisor(profile=CONFIG["SPEED_PROFILES"]["test_speed"], linear_speed=0.0,
                                        angular_speed=0.0)
        supervisor.set_trajectory(path)

        super().__init__(logger, self)

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def rolling_basis_state(self):
        """
        Get the state of the rolling basis
        """
        self.logger.log(
            f"Rolling basis state:\n"
            f"Odometrie: {self.rolling_basis.odometrie}\n"
            f"Linear Speed: {self.rolling_basis.linear_speed}\n"
            f"Angular Speed:{self.rolling_basis.angular_speed}\n\n",
            LogLevels.DEBUG
        )
        
    @Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
    async def drive_rob(self):
        state = self.supervisor.compute_future_state()

        self.rolling_basis.set_speed_and_position(
            target_linear_speed=state[1],
            target_angular_speed=state[2],
            target_position=state[0]
        )
