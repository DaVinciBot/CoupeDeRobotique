# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSclientRouteManager, WSmsg
from brain import Brain
from utils import Utils


# Import from local path
# from sensors import Lidar
# from controllers import RollingBasis


class Robot1Brain(Brain):
    def __init__(
            self,
            logger: Logger,
            ws_cmd: WSclientRouteManager,
            ws_log: WSclientRouteManager,
            ws_lidar: WSclientRouteManager,
            ws_odometer: WSclientRouteManager,
            ws_camera: WSclientRouteManager
    ) -> None:
        super().__init__(logger, self)

        self.shared = 0

    """
        Routines
    """

    @Brain.task(refresh_rate=1)
    async def main(self):
        print(f"Robot1Brain: {await self.ws_log.receiver.get()} / {self.shared}")
        self.shared += 1
        await self.ws_log.sender.send(
            WSmsg(
                msg="shared",
                data=self.shared
            )
        )
