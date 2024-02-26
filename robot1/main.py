from configuration import APP_CONFIG

from bot import Logger, Lidar, RollingBasis
from bot.Shapes import OrientedPoint

from common.WS import (
    WSclient, WSclientRouteManager,
    WSender, WSreceiver,
    WSmsg
)


async def lidar_bran():
    while True:
        scan = Lidar.scan_to_absolute_cartesian(
            robot_pos=OrientedPoint(
                robot.odometrie.x,
                robot.odometrie.y,
                robot.odometrie.theta
            )
        )
        await lidar.sender.send(
            await lidar.get_ws(),
            WSmsg(
                msg="lidar_scan",
                data=scan
            )
        )
        await asyncio.sleep(1)


async def odometer_brain():
    while True:
        await odometer.sender.send(
            await odometer.get_ws(),
            WSmsg(
                msg="odometer",
                data=[robot.odometrie.x, robot.odometrie.y, robot.odometrie.theta]
            )
        )
        await asyncio.sleep(1)


if __name__ == "__main__":
    # Robot
    robot = RollingBasis()

    # WS connection
    ws_client = WSclient(APP_CONFIG.WS_SERVER_IP, APP_CONFIG.WS_PORT)

    # Lidar
    lidar = WSclientRouteManager(
        WSreceiver(),
        WSender(APP_CONFIG.WS_SENDER_NAME)
    )

    # Log
    log = WServerRouteManager(
        WSreceiver(),
        WSender(APP_CONFIG.WS_SENDER_NAME)
    )

    # Odometer
    odometer = WServerRouteManager(
        WSreceiver(),
        WSender(APP_CONFIG.WS_SENDER_NAME)
    )

    # Bind routes
    ws_client.add_route_handler(APP_CONFIG.WS_LIDAR_ROUTE, lidar)
    ws_client.add_route_handler(APP_CONFIG.WS_LOG_ROUTE, log)
    ws_client.add_route_handler(APP_CONFIG.WS_ODOMETER_ROUTE, odometer)

    # Add background tasks
    ws_client.add_background_task(lidar_brain)
    ws_client.add_background_task(odometer_brain)

    ws_client.run()
