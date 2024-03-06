import math
import cv2


class PlanTransposer:
    def __init__(self, camera_table_distance, alpha, beta):
        self.camera_table_distance = camera_table_distance
        self.alpha = alpha
        self.beta = beta

    def image_distance_to_relative_distance(self, segment):
        try:
            distance_camera_object_on_table = self.alpha * math.pow(segment, self.beta)
            # Il faut peut être mettre juste un abs avant de faire la racine carré ! (pas sur)

            # We use Pythagoras to find the real distance between the camera and
            # the object from the table's point of view.
            real_distance_camera_object = math.sqrt(
                math.pow(distance_camera_object_on_table, 2)
                - math.pow(self.camera_table_distance, 2)
            )
        except Exception as error:
            print(f"Error during real_distance_camera_object computation [{error}]")
            real_distance_camera_object = -1

        return real_distance_camera_object

    def image_to_relative_position(self, img, segment, center_point):
        """
        To transpose the image coordinates to a relative position on the table
        we need a distance (it is the max radius ellipse in our case)
        and the center point of our object (it is the barycenter of our ellipse)
        :param img:
        :param segment:
        :param center_point:
        :return:
        """

        # Get relative distance between the camera and the object
        distance_object_camera = self.image_distance_to_relative_distance(segment)

        # Get the distance between the camera and the object projected on center of the image
        distance_camera_center_object = center_point[0] - img.shape[1] / 2
        # Convert this distance to a real distance
        k = 0.001285
        distance_camera_center_object = (
            distance_camera_center_object * k * distance_object_camera
        )

        # Compute the relative position of the object
        x = distance_camera_center_object
        y = math.sqrt(
            math.pow(distance_object_camera, 2)
            - math.pow(distance_camera_center_object, 2)
        )

        return x, y
