# Import from common
import asyncio
import time

from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSmsg, WServerRouteManager
from brain import Brain

# Import from local path
from sensors import Camera, ArucoRecognizer, ColorRecognizer, PlanTransposer, Frame

import matplotlib.pyplot as plt


class ServerBrain(Brain):
    """
    This brain is the main controller of the server.
    """

    def __init__(
            self,
            logger: Logger,
            ws_cmd: WServerRouteManager,
            ws_log: WServerRouteManager,
            ws_lidar: WServerRouteManager,
            ws_odometer: WServerRouteManager,
            ws_camera: WServerRouteManager,
            arena: MarsArena,
            config
    ) -> None:
        self.shared = 0
        self.arucos = []
        self.green_objects = []

        super().__init__(logger, self)

    """
        Routines
    """

    @Brain.task(process=True, run_on_start=True, timeout=10, define_loop_later=True, refresh_rate=1)
    def test(self):
        local_var = 0

        # ---Loop--- #
        print("test, BEFORE: ", local_var)
        local_var += 1
        print("test, AFTER: ", local_var)

    @Brain.task(process=False, run_on_start=True)
    async def main(self):
        print("Main start")
        #print("OUTPUT:", await self.test())
        #print("OUTPUT:", await self.test())
        print("Main end", self.shared)
