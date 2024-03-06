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
        ws_lidar: WServerRouteManager,
        ws_odometer: WServerRouteManager,
        ws_cmd: WServerRouteManager,
        ws_camera: WServerRouteManager,
        ws_log: WServerRouteManager,
        camera: Camera,
        aruco_recognizer: ArucoRecognizer,
        color_recognizer: ColorRecognizer,
        plan_transposer: PlanTransposer,
        arena: MarsArena,
    ) -> None:
        super().__init__(logger, self)

        self.arucos = []
        self.green_objects = []

        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)

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
    async def send_feedback_to_robot1(self):
        robot1 = self.ws_cmd.get_client("robot1")
        if robot1 is not None:
            await self.ws_camera.sender.send(
                WSmsg(
                    msg="camera",
                    data={"arcuo": self.arucos, "green_objects": self.green_objects},
                ),
                clients=robot1,
            )

    @Brain.routine(refresh_rate=1)
    async def update_lidar_scan(self):
        self.lidar_state = await self.ws_lidar.receiver.get()

        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)

        # Décomposition des points en listes de x et y
        x_vals, y_vals = zip(*self.lidar_state.data)
        # Affiche les points
        self.ax.scatter(x_vals, y_vals)

        # Affiche le graphique mis à jour
        plt.draw()
        plt.pause(1)  # Pause pour 1 seconde

    @Brain.routine(refresh_rate=0.5)
    async def main(self):
        # Get the message from routes
        odometer_state = await self.ws_odometer.receiver.get()
        cmd_state = await self.ws_cmd.receiver.get()

        # Log states
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
                    "lidar": self.lidar_state.data,
                    "odometer": odometer_state.data,
                    "cmd": cmd_state.data,
                },
            )
        )
