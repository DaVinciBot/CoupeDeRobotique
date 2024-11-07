import json
import os
import time
from video import MJPEGHandler

import cv2
import imutils
import numpy as np
from imutils.video import VideoStream

from utils import Utils


class Camera:
    def __init__(
        self,
        res_w=800,
        res_h=800,
        captures_path="./",
        undistorted_coefficients_path="",
        skip_warmup=False,
    ):
        self.resolution = [res_h, res_w]
        self.camera = VideoStream(src=0).start()
        self.captures_path = captures_path

        self.undistorted_coefficients_path = undistorted_coefficients_path

        # Wait for the camera to warm up
        if not skip_warmup:
            time.sleep(2.0)

        # Use later
        self.last_record_image = None
        self.undistor_coefficients = dict()

    def chessboard_calibration_images_capture(
        self, save_path, nb_pictures=50, frequency=1
    ):
        total_duration = nb_pictures * frequency

        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        frame_index = 0
        start_timestamp = Utils.get_ts()
        current_timestamp = start_timestamp

        # Picture taking start countdown (5s)
        while current_timestamp - start_timestamp < 5:
            current_timestamp = Utils.get_ts()
            self.capture()
            self.update_monitor(monitor_name="Chessboard calibration")
            print(
                f"Countdown before start of pictures taking: {5 - (current_timestamp - start_timestamp)}"
            )

        start_timestamp = Utils.get_ts()
        current_timestamp = start_timestamp
        last_capture_time = current_timestamp

        # Capture pictures
        while current_timestamp - start_timestamp < total_duration:
            self.capture()
            self.update_monitor(monitor_name="Chessboard calibration")
            current_timestamp = Utils.get_ts()

            # Capture a picture every {frequency} seconds
            if current_timestamp - last_capture_time >= frequency:
                self.save(save_path, self.last_record_image)
                frame_index += 1
                last_capture_time = current_timestamp

                print(
                    f"Countdown: {total_duration - (current_timestamp - start_timestamp)}"
                )

    def load_undistor_coefficients(self):
        with open(self.undistorted_coefficients_path) as file:
            self.undistor_coefficients = json.load(file)

    def capture(self):
        self.last_record_image = imutils.resize(
            self.camera.read(), height=self.resolution[0], width=self.resolution[1]
        )

        MJPEGHandler.current_img = self.last_record_image
        return self.last_record_image

    def undistor_image(self):
        # There is some extra computed parameters that we can use
        # -> roi (cropping area) / rotation_vectors / translation_vectors

        self.last_record_image = cv2.undistort(
            src=self.last_record_image,
            cameraMatrix=np.array(self.undistor_coefficients.get("camera_matrix")),
            distCoeffs=np.array(
                self.undistor_coefficients.get("distortion_coefficients")
            ),
            newCameraMatrix=np.array(
                self.undistor_coefficients.get("optimized_camera_matrix")
            ),
        )

    def save(self, save_path=None, image=None, *, name=None):
        if save_path is None:
            save_path = self.captures_path
        if image is None:
            image = self.last_record_image

        file_name = Utils.get_date() if name is None else name
        full_path = os.path.join(save_path, f"{file_name}.jpg")
        cv2.imwrite(full_path, image)

    def update_monitor(self, img=None, monitor_name="Frame"):
        if img is None:
            img = self.last_record_image

        cv2.imshow(monitor_name, img)
        cv2.waitKey(1) & 0xFF

    def get_capture(self):
        return self.last_record_image
