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

        # Route rcvr
        self.ws_cmd_state = WSmsg()
        self.ws_log_state = WSmsg()
        self.ws_lidar_state = WSmsg()
        self.ws_odometer_state = WSmsg()
        self.ws_camera_state = WSmsg()

        self.arucos = []
        self.green_objects = []
        self.lidar_state = []
        self.odometer = []

    """
        Routines
    """

    def __print_new_msg_from_route(self, route_name, msg):
        if msg != WSmsg():
            logger_msg = f"New msg on [{route_name}]: [{msg.sender}] -> [{msg.data}]"
            self.logger.log(logger_msg, LogLevels.INFO)
            self.ws_log.sender.send(WSmsg(msg="Msg received", data=logger_msg))

    @Brain.routine(refresh_rate=0.1)
    async def routes_receiver(self):
        self.ws_cmd_state = await self.ws_cmd.receiver.get()
        self.ws_log_state = await self.ws_log.receiver.get()
        self.ws_lidar_state = await self.ws_lidar.receiver.get()
        self.ws_odometer_state = await self.ws_odoemter.receiver.get()
        self.ws_camera_state = await self.ws_camera.receiver.get()

        self.__print_new_msg_from_route("CMD", self.ws_cmd_state)
        self.__print_new_msg_from_route("LOG", self.ws_log_state)
        self.__print_new_msg_from_route("LIDAR", self.ws_lidar_state)
        self.__print_new_msg_from_route("ODOMETER", self.ws_odometer_state)
        self.__print_new_msg_from_route("CAMERA", self.ws_camera_state)

    """
        Controllers / Sensors feedback processing
    """

    @Brain.routine(refresh_rate=1)
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
    async def update_lidar(self):
        if self.ws_lidar_state != WSmsg:
            self.lidar_state = lidar_msg.data

    @Brain.routine(refresh_rate=0.5)
    async def update_odometer(self):
        if self.ws_odometer_state != WSmsg:
            self.odometer = self.ws_odometer_state.data

    """
        Send computer feedback to associates routes (camera)
    """

    @Brain.routine(refresh_rate=1)
    async def send_camera_to_clients(self):
        await self.ws_camera.sender.send(
            WSmsg(
                msg="camera",
                data={"aruco": self.arucos, "green_objects": self.green_objects},
            )
        )

    """
        Send received command from postman to robot1 (for demo)
    """

    @Brain.routine(refresh_rate=0.1)
    async def send_cmd_to_robot1(self):
        if (
            self.ws_cmd_state != WSmsg()
            and self.ws_cmd.get_client("robot1") is not None
        ):
            await self.ws_cmd.sender.send(
                self.ws_cmd_state, clients=self.ws_cmd.get_client("robot1")
            )


"""    @Brain.routine(refresh_rate=0.5)
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
"""
