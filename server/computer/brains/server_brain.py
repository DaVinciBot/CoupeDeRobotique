# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSmsg, WServerRouteManager
from brain import Brain

# Import from local path
from sensors import Camera, ArucoRecognizer, ColorRecognizer, PlanTransposer, Frame

import matplotlib.pyplot as plt


class ServerBrain(Brain):
    """
    This brain is the main controller of the server.
    """

    def __init__(
        self,
        logger: Logger,
        ws_cmd: WServerRouteManager,
        ws_log: WServerRouteManager,
        ws_lidar: WServerRouteManager,
        ws_odometer: WServerRouteManager,
        ws_camera: WServerRouteManager,
        camera: Camera,
        aruco_recognizer: ArucoRecognizer,
        color_recognizer: ColorRecognizer,
        plan_transposer: PlanTransposer,
        arena: MarsArena,
    ) -> None:
        super().__init__(logger, self)

        self.arucos = []
        self.green_objects = []
        self.lidar_state = []

    """
        Routines
    """

    @Brain.routine(refresh_rate=0.1)
    async def camera_capture(self):
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
            self.green_objects.append(green_object.centroid)

        frame = Frame(self.camera.get_capture(), [green_objects, arucos])
        frame.draw_markers()
        frame.write_labels()
        self.camera.update_monitor(frame.img)

    @Brain.routine(refresh_rate=0.5)
    async def send_camera_to_clients(self):
        await self.ws_camera.sender.send(
            WSmsg(
                msg="camera",
                data={"aruco": self.arucos, "green_objects": self.green_objects},
            )
        )

    @Brain.routine(refresh_rate=0.5)
    async def transmit_cmd_to_robot1(self):
        cmd = await self.ws_cmd.receiver.get()
        if cmd != WSmsg():
            await self.ws_cmd.sender.send(cmd)

    @Brain.routine(refresh_rate=0.5)
    async def update_lidar(self):
        lidar_msg = await self.ws_lidar.receiver.get()
        if lidar_msg != WSmsg():
            self.lidar_state = lidar_msg.data

    @Brain.routine(refresh_rate=0.5)
    async def main(self):
        # Get the message from routes
        odometer_state = await self.ws_odometer.receiver.get()

        # Log states
        self.logger.log(f"Odometer state: {odometer_state}", LogLevels.INFO)
        if isinstance(self.lidar_state, list):
            self.logger.log(f"Lidar state: {len(self.lidar_state)}", LogLevels.INFO)
        self.logger.log(f"Recognized aruco number: {len(self.arucos)}", LogLevels.INFO)

        # Send log to all clients
        await self.ws_log.sender.send(
            WSmsg(
                msg="States",
                data={
                    "arucos": self.arucos,
                    "green_objects": self.green_objects,
                    "lidar": self.lidar_state,
                    "odometer": odometer_state.data,
                },
            )
        )
