# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSmsg, WServerRouteManager
from brain import Brain

# Import from local path
from controllers import Camera, ArucoRecognizer, ColorRecognizer, PlanTransposer


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
            color_recognizer: ColorRecognizer,
            plan_transposer: PlanTransposer,

            arena: MarsArena
    ) -> None:
        super().__init__(logger, self)

        self.arucos = []
        self.green_objects = []

    """
        Routines
    """

    @Brain.routine(refresh_rate=1)
    async def camera_capture(self):
        self.logger.log("Server Brain-camera_capture is working", LogLevels.INFO)

        self.camera.capture()
        self.camera.undistor_image()
        arucos = self.aruco_recognizer.detect(self.camera.get_capture())
        green_objects = self.color_recognizer.detect(self.camera.get_capture())

        self.arucos = []
        for aruco in arucos:
            self.arucos.append(
                (
                    aruco.encoded_number,
                    self.plan_transposer.image_to_relative_position(
                        img=self.camera.get_capture(),
                        segment=aruco.max_radius,
                        center_point=aruco.centroid,
                    ),
                )
            )

        self.green_objects = []
        for green_object in green_objects:
            self.green_objects.append(
                green_object.centroid
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
                    "green_objects": self.green_objects,
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
