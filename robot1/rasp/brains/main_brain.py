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
# from led_strip import LEDStrip
from utils import Utils
# from GPIO import PIN

# Import from local path
from utils import LidarMode, AntiCollisionHandle, GoToResult
# from controllers import RollingBasis, Actuators
from sensors import Lidar


@dataclass
class Objective:
    task: str  # objective type ("pickup","drop_to_zone","drop_to_gardener")
    target_index: int  # index of the target
    time_estimate: float = -1.0  # time estimate (won't try if it's too late)
    elevator_after: str = ""

    def __str__(self):
        r = f"{self.task}, at {self.target_index}, estimated time: {self.time_estimate}"
        match self.elevator_after:
            case "top":
                r += ", then raising elevator for next objective"
            case "bottom":
                r += ", then lowering elevator for next objective"
            case "intermediate":
                r += ", then setting elevator to intermediate position"
            case _:
                r += ", then nothing"
        return r

    def enough_time(self, start_time) -> bool:

        if (
                Utils.get_ts() + self.time_estimate - start_time > 80
                and self.time_estimate > 0
        ):
            return False
        return True

    def is_interesting(self, arena) -> bool:
        return not (
                (self.task == "pickup")
                and arena.pickup_zones[self.target_index].visited
                and arena.pickup_zones[self.target_index].nb_plant
                < CONFIG.ARENA_CONFIG["limit_plant_pickup"]
        )

    def evaluate(self, start_time, arena) -> bool:
        return self.enough_time(start_time) and self.is_interesting(arena)


class MainBrain(Brain):
    """
    This brain is the main controller of ROB (robot1).
    """

    # Controllers functions
    # from brains.controllers_brain import ()

    # Sensors functions
    # from brains.sensors_brain import ()

    # Com functions
    # from brains.com_brain import zombie_mode

    # Init the brain
    def __init__(
            self,
            logger: Logger,
    ) -> None:
        # Save this for later use (when re-creating the arena)
        self.logger_arena: Logger

        # Init the brain
        super().__init__(logger, self)

        self.logger.log(
            f"Mode: {'zombie' if CONFIG.ZOMBIE_MODE else 'game'}", LogLevels.INFO
        )

    """
        Tasks
    """

    @Brain.task(process=False, run_on_start=True, refresh_rate=1)
    async def coucou(self):
        self.logger.log("Coucou Anne-Marie", LogLevels.INFO)

    @Brain.task(process=True, run_on_start=True, refresh_rate=1)
    def coucou(self):
        self.logger.log("Yo je suis dans un autre process carrément", LogLevels.INFO)
