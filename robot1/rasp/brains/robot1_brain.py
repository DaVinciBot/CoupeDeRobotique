# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSclientRouteManager, WSmsg
from brain import Brain

# Import from local path
from sensors import Lidar
from controllers import RollingBasis

import asyncio


class Robot1Brain(Brain):
    def __init__(
        self,
        logger: Logger,
        arene: MarsArena,
        lidar: Lidar,
        rolling_basis: RollingBasis,
        lidar_ws: WSclientRouteManager,
        odometer_ws: WSclientRouteManager,
        cmd_ws: WSclientRouteManager
    ) -> None:
        super().__init__(logger)

        self.arene = arene
        self.lidar = lidar
        self.rolling_basis = rolling_basis
        self.lidar_ws = lidar_ws
        self.odometer_ws = odometer_ws
        self.cmd_ws = cmd_ws

    async def logical(self):
        # Get controllers feedback
            lidar_scan = self.lidar.scan_to_absolute_cartesian(
                robot_pos=self.rolling_basis.odometrie
            )

            # Get the message from routes
            cmd = await self.cmd_ws.receiver.get()
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

            # Send the controllers feedback to the server
            await self.lidar_ws.sender.send(
                WSmsg(msg="lidar_scan", data=[[s.x, s.y] for s in lidar_scan])
            )
            await self.odometer_ws.sender.send(
                WSmsg(
                    msg="odometer",
                    data=[
                        self.rolling_basis.odometrie.x,
                        self.rolling_basis.odometrie.y,
                        self.rolling_basis.odometrie.theta,
                    ],
                )
            )
            