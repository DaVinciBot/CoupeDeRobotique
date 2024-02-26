from configuration import APP_CONFIG

import asyncio

from WS import WServer, WServerRouteManager, WSender, WSreceiver, WSmsg


async def lidar_brain():
    while True:
        msg = await lidar.receiver.get()
        if msg != WSmsg():
            print(
                f"#--> Message lidar: {msg.msg}, {msg.sender}, {len(msg.data)}, queue: {lidar.receiver.get_queue_size()}"
            )
        else:
            print(f"#--> Message lidar: {msg}")

        await asyncio.sleep(0.1)


if __name__ == "__main__":
    ws_server = WServer(APP_CONFIG.WS_HOSTNAME, APP_CONFIG.WS_PORT)

    # Lidar
    lidar = WServerRouteManager(
        WSreceiver(keep_memory=True, use_queue=True), WSender(APP_CONFIG.WS_SENDER_NAME)
    )

    # Log
    log = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(APP_CONFIG.WS_SENDER_NAME)
    )

    # Odometer
    odometer = WServerRouteManager(
        WSreceiver(keep_memory=True), WSender(APP_CONFIG.WS_SENDER_NAME)
    )

    # Bind routes
    ws_server.add_route_handler(APP_CONFIG.WS_LIDAR_ROUTE, lidar)
    ws_server.add_route_handler(APP_CONFIG.WS_LOG_ROUTE, log)
    ws_server.add_route_handler(APP_CONFIG.WS_ODOMETER_ROUTE, odometer)

    # Add background tasks
    ws_server.add_background_task(lidar_brain)

    ws_server.run()
