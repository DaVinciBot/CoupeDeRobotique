from config_loader import CONFIG

# External imports
import asyncio
import time

# Import from common
from brains import Brain

from ws_comms import WSmsg, WSclientRouteManager, WServerRouteManager
from geometry import OrientedPoint, Point, distance, Polygon, MultiPoint

from loggerplusplus import Logger, LogLevels
import math
from utils import Utils
import matplotlib.pyplot as plt
import time
import numpy as np
import random

# Import from local path
from controllers import RollingBasis, RollingBasisDummy

from path_finding import PathFinder
from arena import ShowArena
from controllers.rolling_basis import (
    RollingBasis,
    RollingBasisDummy
)
from sensors import Lidar, LidarDummy
from remote.remote import PS5Remote


class RemoteBrain(Brain):
    def __init__(
        self,
        logger: Logger,
        # Controllers
        rolling_basis: RollingBasis | RollingBasisDummy,
        # Sensors
        lidar: Lidar | LidarDummy,
        # Remote
        remote: PS5Remote,
        # WS routes
        ws_cmd: WServerRouteManager,
    ) -> None:
        if isinstance(rolling_basis, RollingBasisDummy):
            logger.log("RollingBasisDummy is used", LogLevels.WARNING)

        # Controllers
        self.rolling_basis: RollingBasis = rolling_basis
        self.rolling_basis.set_angular_position_pid(0, 0, 0)
        self.rolling_basis.set_linear_position_pid(0, 0, 0)
        # Sensors
        self.lidar: Lidar = lidar
        # Remote
        self.remote: PS5Remote = remote
        logger.log("Waiting for remote connection", LogLevels.INFO)
        self.remote.connect()
        logger.log("Remote connected", LogLevels.INFO)

        # WS routes
        self.ws_cmd: WServerRouteManager = ws_cmd

        super().__init__(logger, self)

        # Attributes for the visualization
        self.fig, self.ax = plt.subplots()

        # TMP for test purpose
        self.lidar_scan_polars = self.lidar.scan_to_polars()

    """ ### Routines ### """

    @Brain.task(
        process=False,
        run_on_start=True,
        refresh_rate=0.1,
        get_is_active_brain=lambda self: self.is_active,
    )
    async def handle_ps5_remote(self):
        self.remote.update()
        self.rolling_basis.set_speed_and_position(
            self.remote.current_linear_speed,
            self.remote.current_rotation_speed,
            OrientedPoint(0, 0),
        )

    @Brain.task(
        process=False,
        run_on_start=CONFIG.ZOMBIE_MODE,
        refresh_rate=0.5,
        get_is_active_brain=lambda self: self.is_active,
    )
    async def zombie_mode(self):
        """
        executes requests received by the server. Use Postman to send request to the server
        Use eval and await eval to run the code you want. Code must be sent as a string
        """
        # Check cmd
        cmd = await self.ws_cmd.receiver.get()

        if cmd != WSmsg():
            self.logger.log(
                f"Zombie instruction {cmd.msg} received: {cmd.data}",
                LogLevels.INFO,
            )

            if cmd.msg == "eval":
                instructions = []
                if isinstance(cmd.data, str):
                    instructions.append(cmd.data)
                elif isinstance(cmd.data, list):
                    instructions = cmd.data

                for instruction in instructions:
                    if instruction.startswith("await "):
                        await eval(instruction.removeprefix("await "))
                    else:
                        eval(instruction)

            else:
                self.logger.log(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                    LogLevels.WARNING,
                )

    """ ### One-Shot Tasks ### """