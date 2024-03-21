# Import from common
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
            camera: Camera,
            aruco_recognizer: ArucoRecognizer,
            color_recognizer: ColorRecognizer,
            plan_transposer: PlanTransposer,
            # arena: MarsArena,
    ) -> None:

        self.shared = 0

        super().__init__(logger, self)

    """
        Routines
    """
    @Brain.task(process=True, refresh_rate=1)
    def writer(self):
        print("writer: ", self.shared)
        self.shared += 1

    @Brain.task(refresh_rate=1)
    async def reader(self):
        print("reader: ", self.shared)



