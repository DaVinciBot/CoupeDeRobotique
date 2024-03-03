# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSmsg, WServerRouteManager
from brain import Brain

# Import from local path
from controllers import Camera, ArucoRecognizer, PlanTransposer


class ServerBrain(Brain):
    """
    This brain is the main controller of the server.
    """

    def __init__(
            self,
            logger: Logger,

            ws_lidar: WServerRouteManager,
            ws_odometer: WServerRouteManager,
            ws_cmd: WServerRouteManager,
            ws_log: WServerRouteManager,

            camera: Camera,
            aruco_recognizer: ArucoRecognizer,
            plan_transposer: PlanTransposer,

            arena: MarsArena
    ) -> None:
        super().__init__(logger, self)

        self.arucos = []

    """
        Routines
    """

    @Brain.routine(refresh_rate=1)
    async def camera_capture(self):
        self.logger.log("Server Brain-camera_capture is working", LogLevels.INFO)

        self.camera.capture()
        self.camera.undistor_image()
        frame = self.aruco_recognizer.detect(self.camera.get_capture())
        ellipses = frame.compute_ellipses()

        self.arucos = []
        # Add arucos to the list following the format: (id, x, y)
        self.arucos.extend(
            (
                int(frame.ids[index][0]),
                self.plan_transposer.image_to_relative_position(
                    img=frame.img,
                    segment=ellipse.get("max_radius"),
                    center_point=ellipse.get("center"),
                ),
            )
            for index, ellipse in enumerate(ellipses)
        )

    @Brain.routine(refresh_rate=1)
    async def main(self):
        self.logger.log("Server Brain-main is working", LogLevels.INFO)

        # Get the message from routes
        lidar_state = await self.ws_lidar.receiver.get()
        odometer_state = await self.ws_odometer.receiver.get()
        cmd_state = await self.ws_cmd.receiver.get()

        # Log states
        self.logger.log(f"Lidar state: {lidar_state}", LogLevels.INFO)
        self.logger.log(f"Odometer state: {odometer_state}", LogLevels.INFO)
        self.logger.log(f"CMD state: {cmd_state}", LogLevels.INFO)
        self.logger.log(f"Recognized aruco number: {len(self.arucos)}", LogLevels.INFO)

        # Send log to all clients
        await self.ws_log.sender.send(
            WSmsg(
                msg="States",
                data={
                    "arucos": self.arucos,
                    "lidar": lidar_state.data,
                    "odometer": odometer_state.data,
                    "cmd": cmd_state.data
                },
            )
        )

        # Send message to Robot1
        robot1 = self.ws_cmd.get_client("robot1")
        if robot1 is not None:
            await self.ws_cmd.sender.send(
                WSmsg(
                    msg="test_cmd",
                    data="coucou",
                ),
                clients=robot1,
            )
