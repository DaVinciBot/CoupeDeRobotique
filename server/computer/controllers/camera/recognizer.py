from controllers.camera.frame import Frame

import numpy as np
import cv2


class ArucoRecognizer:
    def __init__(self, aruco_type: str):
        # Load pre-trained IA from OpenCV based on the aruco type
        self.dictionary = cv2.aruco.Dictionary_get(getattr(cv2.aruco, aruco_type))
        self.params = cv2.aruco.DetectorParameters_create()

    def detect(self, frame: np.ndarray, **extra_params) -> Frame:
        found = cv2.aruco.detectMarkers(frame, self.dictionary, parameters=self.params, **extra_params)
        return Frame(frame, found[1], found[0])
