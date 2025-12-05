"""Module de détection ArUco pour Jetson."""

import math
import time
from typing import Optional

import cv2
import matplotlib as mpl
import numpy as np
from src.camera import Camera
from src.utils.timing import timer

mpl.use("Agg")
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

blue_team_ids = [1, 2, 3, 4, 5]
yellow_team_ids = [6, 7, 8, 9, 10]
marker_600_600_id = 22
marker_600_1400_id = 20
marker_2400_1400_id = 21
marker_2400_600_id = 23
blue_crate_id = 36
yellow_crate_id = 47
empty_crate_id = 41
aire_and_elements_ids = list(range(11, 51))
blue_reserve_ids = list(range(51, 71))
yellow_reserve_ids = list(range(71, 91))


class ArucoDetector:
    """Classe de détection et de localisation des marqueurs ArUco."""

    def __init__(
        self,
        cam: Camera,
        marker_size_cm: float,
        marker_size_ref_cm: float,
        marker_size_crate_cm: float,
        camera_matrix: Optional[np.ndarray] = None,
        dist_coeffs: Optional[np.ndarray] = None,
        assumed_hfov_deg: float = 60.0,
    ) -> None:
        """Initialise l'instance de détection ArUco.

        Args:
            cam (Camera): La caméra utilisée pour la détection.
            marker_size_cm (float): La taille du marqueur en centimètres.
            marker_size_ref_cm (float): Taille du marqueur de référence en centimètres.
            marker_size_crate_cm (float): La taille du marqueur de crate en centimètres.
            camera_matrix (np.ndarray | None, optional): La matrice de la caméra.
            dist_coeffs (np.ndarray | None, optional): Les coefficients de distorsion.
            assumed_hfov_deg (float, optional): Champ vision horizontal supposé en deg.
        """
        self.cam = cam
        self.marker_size_m = float(marker_size_cm) / 100.0
        self.marker_size_ref_m = float(marker_size_ref_cm) / 100.0
        self.marker_size_crate_m = float(marker_size_crate_cm) / 100.0

        self.size_mapping = {}
        for mid in [20, 21, 22, 23]:
            self.size_mapping[mid] = self.marker_size_ref_m
        for mid in [36, 41, 47]:
            self.size_mapping[mid] = self.marker_size_crate_m

        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.assumed_hfov_deg = float(assumed_hfov_deg)

        self._arena_fig = None
        self._arena_ax = None
        self._arena_canvas = None

        # OpenCV 4.5.1 compatible API
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        self.aruco_params = cv2.aruco.DetectorParameters_create()

        if self.camera_matrix is None:
            w, h = self.cam.get_resolution()
            if w and h:
                fx = fy = (w / 2.0) / math.tan(
                    math.radians(self.assumed_hfov_deg) / 2.0,
                )
                self.camera_matrix = np.array(
                    [[fx, 0.0, w / 2.0], [0.0, fy, h / 2.0], [0.0, 0.0, 1.0]],
                    dtype=np.float64,
                )
                self.dist_coeffs = (
                    np.zeros((5, 1), dtype=np.float64)
                    if self.dist_coeffs is None
                    else self.dist_coeffs
                )

        # Positions de référence en mètres (centre des marqueurs)
        self.ref_markers_world = {
            20: np.array([0.600, 1.400]),  # Sans Z
            21: np.array([2.400, 1.400]),
            22: np.array([0.600, 0.600]),
            23: np.array([2.400, 0.600]),
        }

        # Matrices de transformation
        self.homography_matrix = None
        self.affine_matrix = None
        self.transform_computed = False
        self.transform_type = None

        self.last_seen_refs = {}
        self.ref_cache_timeout = 20.0

    def get_marker_size(self, marker_id: int) -> float:
        """Retourne la taille du marqueur en mètres selon son ID.

        Args:
            marker_id (int): L'ID du marqueur.

        Returns:
            float: La taille du marqueur en mètres.
        """
        return self.size_mapping.get(marker_id, self.marker_size_m)

    def get_objp_for_marker(self, marker_id: int) -> np.ndarray:
        """Retourne les points 3D du marqueur selon son ID.

        Args:
            marker_id (int): L'ID du marqueur.

        Returns:
            np.ndarray: Les points 3D du marqueur.
        """
        size = self.get_marker_size(marker_id)
        s = size / 2.0
        return np.array(
            [[-s, -s, 0.0], [s, -s, 0.0], [s, s, 0.0], [-s, s, 0.0]],
            dtype=np.float64,
        )

    @staticmethod
    def convert_world_coords_mm(pos_world: np.ndarray) -> str:
        """Convertit les coordonnées du monde en millimètres.

        Args:
            pos_world (np.ndarray): Les coordonnées du monde en mètres.

        Returns:
            str: Les coordonnées formatées en millimètres.
        """
        x_mm = round(float(pos_world[0]) * 1000.0)
        y_mm = round(float(pos_world[1]) * 1000.0)
        return f"{x_mm},{y_mm}"

    def convert_id_to_name(self, marker_id: int) -> str:
        """Convertit un ID de marqueur en nom lisible.

        Args:
            marker_id (int): L'ID du marqueur.

        Returns:
            str: Le nom lisible du marqueur.
        """
        if marker_id in blue_team_ids:
            return "Equipe Bleue"
        if marker_id in yellow_team_ids:
            return "Equipe Jaune"
        if marker_id == marker_600_1400_id:
            return "Aire de jeu 600, 1400"
        if marker_id == marker_2400_1400_id:
            return "Aire de jeu 2400, 1400"
        if marker_id == marker_600_600_id:
            return "Aire de jeu 600, 600"
        if marker_id == marker_2400_600_id:
            return "Aire de jeu 2400, 600"
        if marker_id == blue_crate_id:
            return "Caisse bleue"
        if marker_id == yellow_crate_id:
            return "Caisse jaune"
        if marker_id == empty_crate_id:
            return "Caisse vide"
        if aire_and_elements_ids[0] <= marker_id <= aire_and_elements_ids[-1]:
            return "Aire de jeu et elements"
        if blue_reserve_ids[0] <= marker_id <= blue_reserve_ids[-1]:
            return "Reserves Equipe Bleue"
        if yellow_reserve_ids[0] <= marker_id <= yellow_reserve_ids[-1]:
            return "Reserves Equipe Jaune"

        return "ID invalide"

    @timer
    def compute_transform_from_refs(self, corners, ids, use_cache=True):
        """
        Calcule la transformation image -> monde.
        Nécessite au moins 3 références (peut compléter depuis un cache).
        """
        src_points = []
        dst_points = []
        current_time = time.time()

        # Collecte des marqueurs visibles et mise à jour du cache
        for i, marker_id in enumerate(ids):
            mid = int(marker_id[0])
            if mid in self.ref_markers_world:
                center = np.mean(corners[i][0], axis=0)
                src_points.append(center)
                world_pos = self.ref_markers_world[mid] * 1000.0
                dst_points.append(world_pos)

                # Met à jour le cache de visibilité
                self.last_seen_refs[mid] = (center, current_time)

        # Si pas assez de références, compléter depuis le cache valide
        if use_cache and len(src_points) <= 3:
            for mid, world_pos_m in self.ref_markers_world.items():
                if mid in self.last_seen_refs:
                    cached_center, cached_time = self.last_seen_refs[mid]

                    # Ignorer si le cache est expiré
                    if current_time - cached_time <= self.ref_cache_timeout:
                        # Ne pas dupliquer une référence déjà présente
                        if mid not in [
                            int(ids[i][0])
                            for i in range(len(ids))
                            if int(ids[i][0]) in self.ref_markers_world
                        ]:
                            src_points.append(cached_center)
                            world_pos = world_pos_m * 1000.0
                            dst_points.append(world_pos)

                            # Limiter à 4 références
                            if len(src_points) >= 4:
                                break

        num_refs = len(src_points)

        if num_refs < 3:
            self.transform_computed = False
            self.transform_type = None
            return False

        src_pts = np.array(src_points, dtype=np.float32)
        dst_pts = np.array(dst_points, dtype=np.float32)

        try:
            if num_refs >= 4:
                self.homography_matrix, _ = cv2.findHomography(
                    src_pts, dst_pts, cv2.RANSAC, 5.0
                )
                if self.homography_matrix is None:
                    self.transform_computed = False
                    self.transform_type = None
                    return False
                self.transform_type = "homography"
                self.affine_matrix = None

            else:  # num_refs == 3
                self.affine_matrix = cv2.getAffineTransform(src_pts, dst_pts)
                self.transform_type = "affine"
                self.homography_matrix = None

            self.transform_computed = True
            return True

        except Exception:
            self.transform_computed = False
            self.transform_type = None
            return False

    def transform_point_to_world(self, image_point):
        """
        Projette un point image vers les coordonnées monde (m).
        Utilise homographie ou transformée affine selon disponibilité.
        """
        if not self.transform_computed:
            return None

        if self.transform_type == "homography" and self.homography_matrix is not None:
            # Homographie
            pt = np.array([image_point[0], image_point[1], 1.0])
            world_pt = self.homography_matrix @ pt
            world_pt = world_pt[:2] / world_pt[2]
            return world_pt / 1000.0

        elif self.transform_type == "affine" and self.affine_matrix is not None:
            # Affine
            pt = np.array([image_point[0], image_point[1], 1.0])
            world_pt = self.affine_matrix @ pt
            return world_pt / 1000.0

        return None

    @timer
    def _init_arena_plot(self, arena_size_mm=(3000, 2000)):
        ARENA_W, ARENA_H = int(arena_size_mm[0]), int(arena_size_mm[1])

        self._arena_fig = plt.figure(figsize=(10, 7), dpi=100)
        self._arena_ax = self._arena_fig.add_subplot(1, 1, 1)
        self._arena_ax.set_xlim(0, ARENA_W)
        self._arena_ax.set_ylim(0, ARENA_H)
        self._arena_ax.set_aspect("equal")
        self._arena_ax.set_xlabel("X (mm)")
        self._arena_ax.set_ylabel("Y (mm)")
        self._arena_ax.set_title(f"Arène {ARENA_W}x{ARENA_H} mm - ArUco")
        self._arena_ax.grid(True, linestyle="--", alpha=0.25)

        rect = patches.Rectangle(
            (0, 0), ARENA_W, ARENA_H, linewidth=2, edgecolor="black", facecolor="none"
        )
        self._arena_ax.add_patch(rect)

        plt.tight_layout()
        self._arena_canvas = FigureCanvas(self._arena_fig)

    @timer
    def update_arena_display(
        self,
        detected_world=None,
        marker_size_mm=200.0,
        arrow_len_mm=300.0,
        window_name="Arena",
    ):
        if self._arena_fig is None:
            self._init_arena_plot()

        detected_world = detected_world or []  # Liste vide par défaut

        self._arena_ax.clear()

        ARENA_W, ARENA_H = 3000, 2000
        self._arena_ax.set_xlim(0, ARENA_W)
        self._arena_ax.set_ylim(0, ARENA_H)
        self._arena_ax.set_aspect("equal")
        self._arena_ax.set_xlabel("X (mm)")
        self._arena_ax.set_ylabel("Y (mm)")
        self._arena_ax.set_title(f"Arène {ARENA_W}x{ARENA_H} mm - ArUco")
        self._arena_ax.grid(True, linestyle="--", alpha=0.25)

        rect = patches.Rectangle(
            (0, 0), ARENA_W, ARENA_H, linewidth=2, edgecolor="black", facecolor="none"
        )
        self._arena_ax.add_patch(rect)

        for mid, pos_m in self.ref_markers_world.items():
            x_mm = float(pos_m[0]) * 1000.0
            y_mm = float(pos_m[1]) * 1000.0
            circle = patches.Circle(
                (x_mm, y_mm), 80, color="red", fill=False, linewidth=2, linestyle="--"
            )
            self._arena_ax.add_patch(circle)

        cmap = plt.get_cmap("tab10")
        legend_handles = []

        for idx, (mid, pos_m, yaw) in enumerate(detected_world):
            if mid in self.ref_markers_world:
                color = "green"
                alpha = 0.6
            else:
                color = cmap(idx % 10)
                alpha = 0.9

            x_mm = float(pos_m[0]) * 1000.0
            y_mm = float(pos_m[1]) * 1000.0

            if (
                x_mm < -500
                or x_mm > ARENA_W + 500
                or y_mm < -500
                or y_mm > ARENA_H + 500
            ):
                continue

            s = marker_size_mm * 0.6
            lower_left = (x_mm - s / 2.0, y_mm - s / 2.0)
            square = patches.Rectangle(
                lower_left,
                s,
                s,
                linewidth=1,
                edgecolor="k",
                facecolor=color,
                alpha=alpha,
            )
            self._arena_ax.add_patch(square)

            dx = math.cos(yaw) * arrow_len_mm
            dy = math.sin(yaw) * arrow_len_mm
            self._arena_ax.arrow(
                x_mm,
                y_mm,
                dx,
                dy,
                head_width=60,
                head_length=60,
                fc="k",
                ec="k",
                length_includes_head=True,
            )

            name = self.convert_id_to_name(mid)
            self._arena_ax.text(
                x_mm + s / 2 + 6,
                y_mm - s / 2 - 3,
                f"{mid}: {name}\n({x_mm:.0f}, {y_mm:.0f})",
                fontsize=9,
                color="black",
                verticalalignment="bottom",
            )

            handle = mlines.Line2D(
                [],
                [],
                marker="s",
                color="w",
                markerfacecolor=color,
                markersize=8,
                label=f"{mid}: {name} ({x_mm:.0f}, {y_mm:.0f})",
            )
            legend_handles.append(handle)

        if legend_handles:
            self._arena_ax.legend(
                handles=legend_handles,
                loc="center left",
                bbox_to_anchor=(1.01, 0.5),
                frameon=True,
                fontsize=9,
            )

        try:
            self._arena_canvas.draw()
            buf = self._arena_canvas.buffer_rgba()
            img_rgba = np.asarray(buf)
            img_bgr = cv2.cvtColor(img_rgba, cv2.COLOR_RGBA2BGR)
            img_bgr = np.ascontiguousarray(img_bgr)
            cv2.imshow(window_name, img_bgr)
        except Exception:
            pass

    @timer
    def analyze_frame(self, frame, show_arena=True, arena_window_name="Arena"):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # OpenCV 4.5.1 compatible API: utiliser detectMarkers directement
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params
        )

        if ids is None or len(ids) == 0:
            if show_arena:
                self.update_arena_display(
                    detected_world=[], window_name=arena_window_name
                )
            return frame, []

        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        self.compute_transform_from_refs(corners, ids, use_cache=True)

        detected_world = []  # Liste au lieu de dictionnaire

        if self.transform_computed:
            for i in range(len(ids)):
                mid = int(ids[i][0])
                name = self.convert_id_to_name(mid)
                center_img = np.mean(corners[i][0], axis=0)
                center_display = center_img.astype(int)
                pos_world = self.transform_point_to_world(center_img)

                if pos_world is not None:
                    corner0_world = self.transform_point_to_world(corners[i][0][0])
                    corner1_world = self.transform_point_to_world(corners[i][0][1])

                    if corner0_world is not None and corner1_world is not None:
                        vec_world = corner1_world - corner0_world
                        yaw = math.atan2(vec_world[1], vec_world[0]) + math.pi / 2.0
                        while yaw > math.pi:
                            yaw -= 2 * math.pi
                        while yaw < -math.pi:
                            yaw += 2 * math.pi
                    else:
                        yaw = 0.0

                    coord_str = ArucoDetector.convert_world_coords_mm(pos_world)
                    cache_indicator = ""
                    if mid in self.ref_markers_world:
                        visible_refs = [
                            int(ids[j][0])
                            for j in range(len(ids))
                            if int(ids[j][0]) in self.ref_markers_world
                        ]
                        if len(visible_refs) < 3:
                            cache_indicator = " (cache)"

                    cv2.putText(
                        frame,
                        coord_str + cache_indicator,
                        (center_display[0] - 50, center_display[1] + 12),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (10, 180, 10),
                        2,
                    )
                    cv2.putText(
                        frame,
                        f"{math.degrees(yaw):.1f}deg",
                        (center_display[0] - 50, center_display[1] + 26),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (10, 180, 10),
                        2,
                    )
                    cv2.putText(
                        frame,
                        f"{name}",
                        (center_display[0] - 50, center_display[1] - 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 150),
                        2,
                    )

                    # Ajouter un tuple (ID, position, yaw)
                    detected_world.append((mid, pos_world, yaw))
        else:
            for i in range(len(ids)):
                mid = int(ids[i][0])
                name = self.convert_id_to_name(mid)
                center = np.mean(corners[i][0], axis=0).astype(int)
                cv2.putText(
                    frame,
                    f"{name}",
                    (center[0] - 50, center[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )
                cv2.putText(
                    frame,
                    "Need refs (min 3)",
                    (center[0] - 60, center[1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 0, 255),
                    2,
                )

        if show_arena:
            try:
                self.update_arena_display(
                    detected_world=detected_world, window_name=arena_window_name
                )
            except Exception:
                pass

        return frame, detected_world
