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


class MainBrain(Brain):

    def __init__(
        self,
        logger: Logger,
        rolling_basis: RollingBasis
    ) -> None:

        self.rolling_basis: RollingBasis
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
        
    @Brain.task(process=False, run_on_start=True, refresh_rate=0)
    async def drive_rob(self):
        """
        Get the state of the rolling basis
        """
        self.logger.log("Driving the robot...", LogLevels.DEBUG)
        await asyncio.sleep(1)
        self.logger.log("GO !", LogLevels.DEBUG)
        
        self.rolling_basis.set_speed_and_position(
            target_linear_speed = 10.0,
            target_angular_speed = 0.0,
            target_position = OrientedPoint((0.0, 0.0), 0.0)
        )
        
        await asyncio.sleep(1)
        self.logger.log("STOP !", LogLevels.DEBUG)
        
        self.rolling_basis.set_speed_and_position(
            target_linear_speed = 0.0,
            target_angular_speed = 0.0,
            target_position = OrientedPoint((0.0, 0.0), 0.0)
        )
        
        await asyncio.sleep(1)
        self.logger.log("GO BACK !", LogLevels.DEBUG)
        
        self.rolling_basis.set_speed_and_position(
            target_linear_speed = -10.0,
            target_angular_speed = 0.0,
            target_position = OrientedPoint((0.0, 0.0), 0.0)
        )
        
        await asyncio.sleep(1)
        self.logger.log("STOP !", LogLevels.DEBUG)
        
        self.rolling_basis.set_speed_and_position(
            target_linear_speed = 0.0,
            target_angular_speed = 0.0,
            target_position = OrientedPoint((0.0, 0.0), 0.0)
        )
        