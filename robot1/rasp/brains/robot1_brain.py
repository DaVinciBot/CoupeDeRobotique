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
        ws_lidar: WSclientRouteManager,
        ws_odometer: WSclientRouteManager,
        ws_cmd: WSclientRouteManager,
        ws_camera: WSclientRouteManager,
        lidar: Lidar,
        rolling_basis: RollingBasis,
        arena: MarsArena,
    ) -> None:
        super().__init__(logger, self)

        self.lidar_scan = []

    @Brain.routine(refresh_rate=1)
    async def lidar_scan(self):
        self.lidar_scan = self.lidar.scan_to_absolute_cartesian(
            robot_pos=self.rolling_basis.odometrie
        )

    @Brain.routine(refresh_rate=1)
    async def send_feedback_to_server(self):
        await self.ws_lidar.sender.send(
            WSmsg(msg="lidar_scan", data=[[p.x, p.y] for p in self.lidar_scan])
        )
        await self.ws_odometer.sender.send(
            WSmsg(
                msg="odometer",
                data=[
                    self.rolling_basis.odometrie.x,
                    self.rolling_basis.odometrie.y,
                    self.rolling_basis.odometrie.theta,
                ],
            )
        )

    @Brain.routine(refresh_rate=0.5)
    async def main(self):
        # Get the message from routes
        cmd = await self.ws_cmd.receiver.get()
        camera = await self.ws_camera.receiver.get()

        self.logger.log(f"New message from camera: {camera}", LogLevels.INFO)

        if cmd != WSmsg():
            # New command received
            self.logger.log(
                f"Command received: {cmd.msg}, {cmd.sender}, {len(cmd.data)}",
                LogLevels.INFO,
            )
            # Handle it (implemented only for Go_To and Keep_Current_Position)
            if cmd.msg == "Go_To":
                # Verify if the point is accessible
                if MarsArena.enable_go_to(
                    starting_point=Point(
                        self.rolling_basis.odometrie.x, self.rolling_basis.odometrie.y
                    ),
                    destination_point=Point(cmd.data[0], cmd.data[1]),
                ):
                    self.rolling_basis.Go_To(
                        OrientedPoint(cmd.data[0], cmd.data[1], cmd.data[2])
                    )
            elif cmd.msg == "Keep_Current_Position":
                self.rolling_basis.Keep_Current_Position()
            else:
                self.logger.log(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                    LogLevels.WARNING,
                )
