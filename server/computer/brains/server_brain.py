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
        Tasks
    """

    @Brain.task(process=True, run_on_start=True, refresh_rate=1.0)
    def test0(self):
        print("self", self)
        self.shared += 1

        time.sleep(0.4)
        print("Salut TEST0", self.shared)

    @Brain.task(process=False, run_on_start=True, refresh_rate=1.2)
    async def test1(self):
        await asyncio.sleep(0.2)
        print("Salut TEST1", self.shared)

    @Brain.task(process=False, run_on_start=True, refresh_rate=1.4)
    async def test2(self):
        print("Salut TEST2", self.shared)


