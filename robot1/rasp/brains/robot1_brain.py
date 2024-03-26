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
import asyncio


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
        arena: MarsArena,
    ) -> None:
        super().__init__(logger, self)

        self.lidar_values_in_distances = []
        self.lidar_angles = (90, 180)
        self.odometer = None
        self.camera = {}

    """
        Tasks
    """

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
    async def main(self):
        # Check cmd
        cmd = await self.ws_cmd.receiver.get()

        if cmd != WSmsg():
            self.logger.log(f"New cmd received: {cmd}", LogLevels.INFO)

            # Handle it (implemented only for Go_To and Keep_Current_Position)
            if cmd.msg == "Go_To":
                self.rolling_basis.queue = []
                self.rolling_basis.Go_To(
                    position=Point(cmd.data[0], cmd.data[1]),
                    max_speed=cmd.data[2],
                    next_position_delay=cmd.data[3],
                    action_error_auth=cmd.data[4],
                    traj_precision=cmd.data[5],
                    correction_trajectory_speed=cmd.data[6],
                    acceleration_start_speed=cmd.data[7],
                    acceleration_distance=cmd.data[8],
                    deceleration_end_speed=cmd.data[9],
                    deceleration_distance=cmd.data[10],
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

