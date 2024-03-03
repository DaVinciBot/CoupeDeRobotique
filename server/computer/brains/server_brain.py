# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSmsg, WServerRouteManager
from brain import Brain

# Import from local path
from controllers import Camera, ArucoRecognizer, PlanTransposer

import asyncio


class ServerBrain(Brain):
    def __init__(
            self,
            logger: Logger,

            ws_lidar: WServerRouteManager,
            ws_odometer: WServerRouteManager,
            ws_cmd: WServerRouteManager,
            camera: Camera,
            aruco_recognizer: ArucoRecognizer,
            plan_transposer: PlanTransposer,
            arena: MarsArena
    ) -> None:
        super().__init__(logger)

        self.ws_lidar = ws_lidar
        self.ws_odometer = ws_odometer
        self.ws_cmd = ws_cmd
        self.camera = camera
        self.aruco_recognizer = aruco_recognizer
        self.plan_transposer = plan_transposer
        self.arena = arena

    def get_aruco_pos(self):
        self.camera.capture()
        self.camera.undistor_image()
        frame = self.aruco_recognizer.detect(self.camera.get_capture())
        ellipses = frame.compute_ellipses()

        return [
            self.plan_transposer.image_to_relative_position(
                img=frame.img,
                segment=ellipse.get("max_radius"),
                center_point=ellipse.get("center"),
            )
            for ellipse in ellipses
        ]

    async def logical(self):
        self.logger.log("Server Brain is working", LogLevels.INFO)

        # Get the message from routes
        lidar_state = await self.ws_lidar.receiver.get()
        odometer_state = await self.ws_odometer.receiver.get()
        cmd_state = await self.ws_cmd.receiver.get()

        # Get feedback from controllers
        arucos = self.get_aruco_pos()

        # Log states
        self.logger.log(f"Lidar state: {lidar_state}", LogLevels.INFO)
        self.logger.log(f"Odometer state: {odometer_state}", LogLevels.INFO)
        self.logger.log(f"CMD state: {cmd_state}", LogLevels.INFO)
        self.logger.log(f"Recognized aruco number: {len(arucos)}", LogLevels.INFO)

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

        await asyncio.sleep(1)
