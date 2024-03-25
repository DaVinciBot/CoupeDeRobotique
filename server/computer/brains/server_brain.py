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
            config
    ) -> None:

        self.shared = 0
        self.arucos = []
        self.green_objects = []

        super().__init__(logger, self)

    """
        Routines
    """

    @Brain.task(process=True, refresh_rate=3, define_loop_later=True)
    def test_process_cutter(self):
        camera = Camera(
            res_w=self.config.CAMERA_RESOLUTION[0],
            res_h=self.config.CAMERA_RESOLUTION[1],
            captures_path=self.config.CAMERA_SAVE_PATH,
            undistorted_coefficients_path=self.config.CAMERA_COEFFICIENTS_PATH,
        )
        camera.load_undistor_coefficients()

        aruco_recognizer = ArucoRecognizer(aruco_type=self.config.CAMERA_ARUCO_DICT_TYPE)

        color_recognizer = ColorRecognizer(
            detection_range=self.config.CAMERA_COLOR_FILTER_RANGE,
            name=self.config.CAMERA_COLOR_FILTER_NAME,
            clustering_eps=self.config.CAMERA_COLOR_CLUSTERING_EPS,
            clustering_min_samples=self.config.CAMERA_COLOR_CLUSTERING_MIN_SAMPLES,
        )

        plan_transposer = PlanTransposer(
            camera_table_distance=self.config.CAMERA_DISTANCE_CAM_TABLE,
            alpha=self.config.CAMERA_CAM_OBJ_FUNCTION_A,
            beta=self.config.CAMERA_CAM_OBJ_FUNCTION_B,
        )

        # ---Loop--- #
        camera.capture()
        camera.undistor_image()
        arucos = aruco_recognizer.detect(camera.get_capture())
        green_objects = color_recognizer.detect(camera.get_capture())

        arucos_tmp = []
        arucos_tmp.extend(
            (
                aruco.encoded_number,
                plan_transposer.image_to_relative_position(
                    img=camera.get_capture(),
                    segment=aruco.max_radius,
                    center_point=aruco.centroid,
                ),
            )
            for aruco in arucos
        )
        self.arucos = arucos_tmp

        green_objects_tmp = []
        green_objects_tmp.extend(
            green_object.centroid for green_object in green_objects
        )
        self.green_objects = green_objects_tmp

        frame = Frame(camera.get_capture(), [green_objects, arucos])
        frame.draw_markers()
        frame.write_labels()
        camera.update_monitor(frame.img)


    @Brain.task(process=True, refresh_rate=1)
    def writer(self):
        print("writer: ", self.shared)
        self.shared += 1

    @Brain.task(refresh_rate=1)
    async def reader(self):
        print("reader: ", self.shared)
        print("arucos: ", self.arucos)
        print("green_objects: ", self.green_objects)
