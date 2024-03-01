# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSclientRouteManager, WSmsg

# Import from local path
from sensors import Lidar
from controllers import RollingBasis

import asyncio


async def robot1_brain(
    logger: Logger,
    arene: MarsArena,
    lidar: Lidar,
    rolling_basis: RollingBasis,
    lidar_ws: WSclientRouteManager,
    odometer_ws: WSclientRouteManager,
    cmd_ws: WSclientRouteManager,
):
    while True:
        try:
            # Get controllers feedback
            lidar_scan = lidar.scan_to_absolute_cartesian(
                robot_pos=rolling_basis.odometrie
            )

            # Get the message from routes
            cmd = await cmd_ws.receiver.get()
            if cmd != WSmsg():
                # New command received
                logger.log(
                    f"Command received: {cmd.msg}, {cmd.sender}, {len(cmd.data)}",
                    LogLevels.INFO,
                )
                # Handle it (implemented only for Go_To and Keep_Current_Position)
                if cmd.msg == "Go_To":
                    # Verify if the point is accessible
                    if MarsArena.enable_go_to(
                        starting_point=Point(
                            rolling_basis.odometrie.x, rolling_basis.odometrie.y
                        ),
                        destination_point=Point(cmd.data[0], cmd.data[1]),
                    ):
                        rolling_basis.Go_To(
                            OrientedPoint(cmd.data[0], cmd.data[1], cmd.data[2])
                        )
                elif cmd.msg == "Keep_Current_Position":
                    rolling_basis.Keep_Current_Position()
                else:
                    logger.log(
                        f"Command not implemented: {cmd.msg} / {cmd.data}",
                        LogLevels.WARNING,
                    )

            # Send the controllers feedback to the server
            await lidar_ws.sender.send(
                WSmsg(msg="lidar_scan", data=[[s.x, s.y] for s in lidar_scan])
            )
            await odometer_ws.sender.send(
                WSmsg(
                    msg="odometer",
                    data=[
                        rolling_basis.odometrie.x,
                        rolling_basis.odometrie.y,
                        rolling_basis.odometrie.theta,
                    ],
                )
            )

        except Exception as e:
            logger.log(f"Server Brain error: {e}", LogLevels.ERROR)
            print("Server Brain error: ", e)

        await asyncio.sleep(1)
