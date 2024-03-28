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

    @Brain.task(process=True, run_on_start=True, refresh_rate=1)
    def test_0(self):
        self.shared += 1
        print("test_0:", self.shared)

    @Brain.task(process=True, run_on_start=True, refresh_rate=1, timeout=10)
    def test_1(self):
        self.shared += 1
        print("test_1:", self.shared)

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.9)
    async def test_2(self):
        print("test_2:", self.shared)

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
    async def main(self):
        cmd_state = await self.ws_cmd.receiver.get()
        # New cmd received !
        if cmd_state != WSmsg():
            print(f"New cmd received ! [{cmd_state}]")
            if self.ws_cmd.get_client("robot1") is not None:
                result = await self.ws_cmd.sender.send(
                    WSmsg(
                        sender="server",
                        msg=cmd_state.msg,
                        data=cmd_state.data
                    ),
                    clients=self.ws_cmd.get_client("robot1")
                )
                print("Result of sending cmd to robot1:", result)

