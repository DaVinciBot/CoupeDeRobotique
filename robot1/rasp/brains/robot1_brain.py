# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSclientRouteManager, WSmsg
from brain import Brain
from utils import Utils

# Import from local path
from sensors import Lidar
from controllers import RollingBasis


class Robot1Brain(Brain):
    def __init__(
        self,
        logger: Logger,
        ws_cmd: WSclientRouteManager,
        ws_log: WSclientRouteManager,
        ws_lidar: WSclientRouteManager,
        ws_odometer: WSclientRouteManager,
        ws_camera: WSclientRouteManager,
        rolling_basis: RollingBasis,
        lidar: Lidar,
        #arena: MarsArena,
    ) -> None:
        super().__init__(logger, self)

        self.lidar_scan = []
        self.odometer = []
        self.camera = {}

    """
        Routines
    """

    """
        Get controllers / sensors feedback (odometer / lidar + extern (camera))
    """

    @Brain.task(refresh_rate=0.5)
    async def lidar_scan(self):
        scan = self.lidar.scan_to_absolute_cartesian(
            robot_pos=self.rolling_basis.odometrie
        )

        self.lidar_scan = [[p.x, p.y] for p in scan]


    """
        Send controllers / sensors feedback (odometer / lidar)
    """

    @Brain.task(refresh_rate=1)
    async def send_lidar_scan_to_server(self):
        if self.lidar_scan:
            await self.ws_lidar.sender.send(
                WSmsg(msg="lidar_scan", data=self.lidar_scan)
            )

    @Brain.task(refresh_rate=1)
    async def send_odometer_to_server(self):
        if self.odometer:
            await self.ws_odometer.sender.send(
                WSmsg(msg="odometer", data=self.odometer)
            )

    @Brain.task(refresh_rate=0.1)
    async def main(self):
        # Check cmd
        cmd = await self.ws_cmd.receiver.get()

        if cmd != WSmsg():
            self.logger.log(f"New cmd received: {cmd}", LogLevels.INFO)

            # Handle it (implemented only for Go_To and Keep_Current_Position)
            if cmd.msg == "Go_To":
                self.rolling_basis.queue = []
                self.rolling_basis.Go_To(
                    OrientedPoint(cmd.data[0], cmd.data[1], cmd.data[2]),
                    skip_queue=True,
                )
            elif cmd.msg == "Keep_Current_Position":
                self.rolling_basis.queue = []
                self.rolling_basis.Keep_Current_Position()

            elif cmd.msg == "Set_PID":
                self.rolling_basis.queue = []
                self.rolling_basis.Set_PID(Kp=cmd.data[0], Ki=cmd.data[1], Kd=cmd.data[2])

            else:
                self.logger.log(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                    LogLevels.WARNING,
                )
