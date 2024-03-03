import cv2
import numpy as np
import glob
import json
import os


class CameraCalibrator:
    """
    CameraCalibrator class is used to calibrate the camera using the chessboard images.
    It will compute the camera matrix, distortion coefficients, rotation and translation vectors.
    """

    def __init__(self, calibration_images_path: str, chessboard_size: tuple[int, int], chess_square_size: float,
                 coefficient_path: str):
        self.calibration_images_path = calibration_images_path
        self.chessboard_size = chessboard_size
        # If square size in meters => output result of markers detection will be in meters
        self.chess_square_size = chess_square_size
        self.coefficient_path = coefficient_path

        # Define all the class variables which will be used to compute undistorted coef
        # Criteria for termination of the iterative process of corner refinement
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Create ref points (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0) -> 3D
        # They are the theoretic real world points with which we will compare image's points.
        self.th_pts_3D = np.zeros(
            (self.chessboard_size[0] * self.chessboard_size[1], 3),
            np.float32
        )
        # Associate each point to a grid position
        self.th_pts_3D[:, :2] = np.mgrid[
                                0:self.chessboard_size[0],
                                0:self.chessboard_size[1]
                                ].T.reshape(-1,
                                            2) * self.chess_square_size  # 3D points in real world space according to the chessboard square size reference

        self.img_pts = []  # 2d points in image plane.
        self.th_pts = []  # 3d points in real world space

        # Others variables which will be used later
        self.camera_matrix = None
        self.optimized_camera_matrix = None
        self.distortion_coefficients = None
        self.rvecs = None
        self.tvecs = None
        self.roi = None
        self.calibration_images = []
        self.processed_image_sample = None

    def load_images(self):
        self.calibration_images = glob.glob(f"{os.path.join(self.calibration_images_path, '*')}.jpg")
        if self.calibration_images is None or len(self.calibration_images) == 0:
            print("WARNING: no pictures found !")

    def chessboard_detection(self, convert_to_gray=True, save_processed_images=False, processed_images_path=""):
        if not self.calibration_images:
            print("No images loaded ! EXIT")
            return False

        found_count = 0
        for img_path in self.calibration_images:
            img = cv2.imread(img_path)

            # Convert to gray, to increase the chessboard detection accuracy
            if convert_to_gray and len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img

            # Find the chess board corners
            finding_success, corners = cv2.findChessboardCorners(
                gray,
                self.chessboard_size,
                None
            )

            # Continue only if a chess board was found
            if finding_success:
                found_count += 1

                # Refine the result to be more precise
                precise_corners = cv2.cornerSubPix(
                    gray,
                    corners,
                    (11, 11),
                    (-1, -1),
                    self.criteria
                )

                # Save the refined corners
                self.img_pts.append(precise_corners)
                self.th_pts.append(self.th_pts_3D)

                # Save the processed image as sample (it will be used to get the image size)
                self.processed_image_sample = gray

                # Draw the corners on the input image
                img = cv2.drawChessboardCorners(img, self.chessboard_size, precise_corners, True)

                # Save the processed image
                if save_processed_images:
                    if processed_images_path == "":
                        save_path = self.calibration_images_path
                    else:
                        save_path = processed_images_path

                    img_name = os.path.basename(img_path)
                    img_name_ext = split(img_name, ".")
                    cv2.imwrite(
                        os.path.join(save_path, f"{img_name_ext[0]}_processed.{img_name_ext[1]}"),
                        img
                    )
        print(
            f"Found {found_count} chessboards on {len(self.calibration_images)} images. Proportion: {found_count / len(self.calibration_images)}")

    def compute_distortion_coefficients(self, alpha=1):
        # Do the camera calibration help with image's points and theoretics points
        # return -> ret | camera matrix | distortion coefficients | rotation | translation vectors
        _, self.camera_matrix, self.distortion_coefficients, self.rvecs, self.tvecs = cv2.calibrateCamera(
            self.th_pts,
            self.img_pts,
            self.processed_image_sample.shape[::-1],
            None, None
        )

        # Get the optimal camera matrix (remove pixel where the image will be not linear scale)
        # roi is the best cropped to apply if we want a no deformed picture (without black pixel)
        # If the scaling parameter alpha=0, it returns undistorted image with minimum unwanted pixels.
        # So it may even remove some pixels at image corners.
        # If alpha=1, all pixels are retained with some extra black images.
        width, height = self.processed_image_sample.shape[:2]
        self.optimized_camera_matrix, self.roi = cv2.getOptimalNewCameraMatrix(
            self.camera_matrix,
            self.distortion_coefficients,
            (width, height),
            alpha,
            (width, height)
        )

    def save_coefficients(self):
        # Save the coefficients in a json file
        with open(self.coefficient_path, 'w') as file:
            json.dump({
                "camera_matrix": self.camera_matrix.tolist(),
                "optimized_camera_matrix": self.optimized_camera_matrix.tolist(),
                "distortion_coefficients": self.distortion_coefficients.tolist(),
                "roi": self.roi
                #"rotation_vectors": list(self.rvecs),
                #"translation_vectors": list(self.tvecs)
            }, file)
