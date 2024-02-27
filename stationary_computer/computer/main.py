from config_loader import CONFIG

# Import from common
from WS_comms import WServer, WServerRouteManager, WSender, WSreceiver, WSmsg

# Import from local path
# ...

import asyncio


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
    ws_server = WServer(CONFIG.WS_HOSTNAME, CONFIG.WS_PORT)

    # Lidar
    lidar = WServerRouteManager(
        WSreceiver(keep_memory=True, use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )

    # Log
    log = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )

    # Odometer
    odometer = WServerRouteManager(
        WSreceiver(keep_memory=True), WSender(CONFIG.WS_SENDER_NAME)
    )

    # Bind routes
    ws_server.add_route_handler(CONFIG.WS_LIDAR_ROUTE, lidar)
    ws_server.add_route_handler(CONFIG.WS_LOG_ROUTE, log)
    ws_server.add_route_handler(CONFIG.WS_ODOMETER_ROUTE, odometer)

    # Add background tasks
    ws_server.add_background_task(lidar_brain)

    ws_server.run()
