# External imports
# ...

# Import from common
from brain import Brain

from logger import Logger, LogLevels
from geometry import Point
from WS_comms import WSmsg

# Import from local path
from sensors import Camera, ArucoRecognizer, ColorRecognizer, PlanTransposer, Frame


@Brain.task(process=True, run_on_start=True, refresh_rate=0.1, define_loop_later=True)
def camera_capture(self):
    """
    Capture the camera image and detect arucos and green objects.
    """
    camera = Camera(
        res_w=self.config.CAMERA_RESOLUTION[0],
        res_h=self.config.CAMERA_RESOLUTION[1],
        captures_path=self.config.CAMERA_SAVE_PATH,
        undistorted_coefficients_path=self.config.CAMERA_COEFFICIENTS_PATH,
    )

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
    camera.load_undistor_coefficients()

    # Detect pickup zone detection
    camera.capture()
    camera.undistor_image()

    detected_plant_zones = color_recognizer.detect(camera.get_capture())

    pickup_zone = []
    for zone in detected_plant_zones:
        if (zone.bounding_box[1][0] - zone.bounding_box[0][0]) * (
            zone.bounding_box[1][1] - zone.bounding_box[0][1]
        ) > self.config.CAMERA_PICKUP_ZONE_MIN_AREA:
            pickup_zone.append(zone)

    if len(pickup_zone) < 6:
        print("error in zone_plant detection")
    # calculate approximate center and exclude nearest cluster until there is 6 zones remaking

    elif len(pickup_zone) > 6:
        mx = 0
        my = 0
        for z in pickup_zone:
            mx += z.centroid[0]
            my += z.centroid[1]
        apro_center = Point(mx / len(pickup_zone), my / len(pickup_zone))
        pickup_zone = sorted(
            pickup_zone,
            key=lambda zone: apro_center.distance(
                Point(zone.centroid[0], zone.centroid[1])
            ),
        )
        while len(pickup_zone) > 6:
            pickup_zone.pop()

    for zone in pickup_zone:
        print(zone.centroid)

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
    green_objects_tmp.extend(green_object.centroid for green_object in green_objects)
    self.green_objects = green_objects_tmp

    frame = Frame(camera.get_capture(), [green_objects, arucos])
    frame.draw_markers()
    frame.write_centroid()
    camera.update_monitor(frame.img)
