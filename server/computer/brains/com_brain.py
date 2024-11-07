# External imports
# ...

# Import from common
from brain import Brain

from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from WS_comms import WSmsg


# Import from local path
# ...


@Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
async def pami_com(self):
    """
    Send to pami all messages received from the websocket. (Essentially from ROB)
    -> It is this routine that will be used to send to the PAMI the start trigger.
    * This routine send the received message to everyone connected to the PAMI route.
    """
    message = await self.ws_pami.receiver.get()
    if message != WSmsg():
        self.logger.log(
            f"Message received on [PAMI]: {message}. Sending it to PAMIs.",
            LogLevels.DEBUG,
        )
        await self.ws_pami.sender.send(
            WSmsg(sender="server", msg=pami_state.msg, data=pami_state.data),
        )


@Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
async def lidar_com(self):
    """
    Update the lidar points by listening to the LiDAR websocket (message from ROB).
    """
    message = await self.ws_lidar.receiver.get()
    if message != WSmsg():
        self.logger.log(f"Message received on [LiDAR]: {message.msg}.", LogLevels.DEBUG)
        self.lidar_points = [Point(x, y) for x, y in message.data]


@Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
async def odometer_com(self):
    """
    Update ROB position by listening to the odometer websocket (message from ROB).
    """
    message = await self.ws_odometer.receiver.get()
    if message != WSmsg():
        self.logger.log(f"Message received on [Odometer]: {message}.", LogLevels.DEBUG)
        self.rob_pos = OrientedPoint(message.data[0], message.data[1], message.data[2])

        if self.ws_odometer.get_client("WebUI") is not None:
            await self.ws_odometer.sender.send(
                WSmsg(sender="server", msg=message.msg, data=message.data),
                clients=self.ws_odometer.get_client("WebUI"),
            )


@Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
async def camera_com(self):
    """
    Send to all clients connected to the camera route the data captured by the camera.
    (Essentially the arucos and green objects detected)
    """
    # Send Arucos
    await self.ws_camera.sender.send(
        WSmsg(sender="server", msg="arucos", data=self.arucos)
    )
    # Send Green objects
    await self.ws_camera.sender.send(
        WSmsg(sender="server", msg="green_objects", data=self.green_objects)
    )
