import numpy as np
import cv2

from sensors.camera.detected_object import DetectedObject, Aruco, ColorObject


class Frame:
    def __init__(
        self,
        img: np.ndarray,
        detected_object: list[DetectedObject] or list[list[DetectedObject]] = None,
    ):
        self.img = img

        if detected_object is not None:
            if isinstance(detected_object[0], DetectedObject):
                self.detected_object = detected_object
            elif isinstance(detected_object[0], list):
                self.detected_object = []
                for obj_list in detected_object:
                    self.detected_object.extend(obj_list)
            else:
                raise ValueError("Invalid detected_object format")

        self.len = 0 if detected_object is None else len(detected_object)

    @classmethod
    def concat_frames(cls, frames: list, index_of_img_to_keep: int = 0):
        detected_object = []
        for frame in frames:
            detected_object.extend(frame.detected_object)

        return cls(frames[index_of_img_to_keep].img, detected_object)

    def draw_markers(self):
        for obj in self.detected_object:
            cv2.aruco.drawDetectedMarkers(
                self.img, corners=np.array([[obj.corners]], dtype=np.float32)
            )

    def draw_bounding_boxes(self):
        for obj in self.detected_object:
            cv2.rectangle(
                self.img, obj.bounding_box[0], obj.bounding_box[1], (0, 255, 0), 2
            )

    def write_labels(self):
        for obj in self.detected_object:
            cv2.putText(
                self.img,
                obj.__str__(),
                (int(obj.bounding_box[0][0]), int(obj.bounding_box[0][1] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

    def write_centroid(self):
        for obj in self.detected_object:
            cv2.putText(
                self.img,
                f"({obj.centroid[0]:.2f}, {obj.centroid[1]:.2f})",
                (int(obj.bounding_box[0][0]), int(obj.bounding_box[0][1] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
