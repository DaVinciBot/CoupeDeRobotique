"""Module de détection ArUco pour Jetson."""

import math
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import cv2
import numpy as np
from src.arena import arena_elements
from src.camera import CSICamera
from src.utils.timing import timer

# Détection CUDA au chargement du module
_HAS_CUDA = False
try:
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        _HAS_CUDA = True
except AttributeError:
    pass

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
        cam,  # type: CSICamera
        camera_matrix=None,  # type: Optional[np.ndarray]
        dist_coeffs=None,  # type: Optional[np.ndarray]
        assumed_hfov_deg=60.0,  # type: float
    ):  # type: (...) -> None
        """Initialise l'instance de détection ArUco.

        Args:
            cam (CSICamera): La caméra utilisée pour la détection.
            camera_matrix (np.ndarray | None, optional): La matrice de la caméra.
            dist_coeffs (np.ndarray | None, optional): Les coefficients de distorsion.
            assumed_hfov_deg (float, optional): Champ vision horizontal supposé en deg.
        """
        self.cam = cam
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.assumed_hfov_deg = float(assumed_hfov_deg)

        self._arena_fig = None
        self._arena_ax = None
        self._arena_canvas = None

        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        if hasattr(cv2.aruco, "DetectorParameters_create"):
            self.aruco_params = cv2.aruco.DetectorParameters_create()
        else:
            self.aruco_params = cv2.aruco.DetectorParameters()

        # Tuning pour détection maximale de petits marqueurs (3-5cm à ~2m)
        # 7 passes de seuillage adaptatif (au lieu de 3)
        self.aruco_params.adaptiveThreshWinSizeMin = 3
        self.aruco_params.adaptiveThreshWinSizeMax = 23
        self.aruco_params.adaptiveThreshWinSizeStep = 3
        # Accepter les très petits marqueurs (éloignés)
        self.aruco_params.minMarkerPerimeterRate = 0.005
        self.aruco_params.polygonalApproxAccuracyRate = 0.06
        self.aruco_params.minCornerDistanceRate = 0.02
        # Meilleure lecture des petits marqueurs
        self.aruco_params.perspectiveRemovePixelPerCell = 6
        self.aruco_params.perspectiveRemoveIgnoredMarginPerCell = 0.2
        # Correction d'erreur bits plus tolérante
        self.aruco_params.maxErroneousBitsInBorderRate = 0.6
        # Raffinement sub-pixel (stabilise la détection frame-à-frame)
        self.aruco_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        self.aruco_params.cornerRefinementWinSize = 5
        self.aruco_params.cornerRefinementMaxIterations = 30
        self.aruco_params.cornerRefinementMinAccuracy = 0.1

        # CLAHE pour normaliser le contraste (éclairage inégal)
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        # GPU acceleration (Jetson CUDA)
        self.use_cuda = _HAS_CUDA
        if self.use_cuda:
            self.clahe_cuda = cv2.cuda.createCLAHE(
                clipLimit=2.0,
                tileGridSize=(8, 8),
            )
            self._gpu_mat = cv2.cuda_GpuMat()

        # Thread pool pour détection parallèle des tuiles
        self._tile_pool = ThreadPoolExecutor(max_workers=4)

        # Multi-échelle : seuil de marqueurs pour déclencher les tuiles
        self.multiscale_enabled = True
        self.multiscale_min_markers = 50

        # Lissage temporel : carry-forward pour marqueurs statiques
        # {marker_id: (pos_world, yaw, last_seen_time, consecutive_misses)}
        self.marker_history = {}
        self.marker_carry_frames = 2  # Nombre de frames de carry-forward

        # IDs à exclure du carry-forward (mobiles ou déjà cachés)
        self._no_carry_ids = set(
            list(range(1, 11))  # Robots (bleu 1-5, jaune 6-10)
            + [20, 21, 22, 23]  # Références (ont leur propre cache)
        )

        if self.camera_matrix is None and self.cam is not None:
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
            20: np.array([0.600, 1.400]),
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

    def _annotate_marker(
        self,
        frame,
        center_img,
        mid,
        pos_world,
        yaw,
        ids,
        cache_indicator="",
    ):
        """Ajoute les annotations visuelles pour un marqueur sur la frame."""
        coord_str = ArucoDetector.convert_world_coords_mm(pos_world)
        center_display = center_img.astype(int)
        name = self.convert_id_to_name(mid)

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
            return "Aire de jeu / elements"
        if blue_reserve_ids[0] <= marker_id <= blue_reserve_ids[-1]:
            return "Reserves Bleue"
        if yellow_reserve_ids[0] <= marker_id <= yellow_reserve_ids[-1]:
            return "Reserves Jaune"

        return "ID invalide"

    @timer
    def compute_transform_from_refs(self, corners, ids, use_cache=True):
        """
        Calcule la transformation image -> monde.
        Nécessite 4 références (peut compléter depuis un cache).
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

    def transform_points_to_world_batch(self, points):
        """Transforme N points image en coordonnées monde (m) en une seule opération.

        Args:
            points: np.ndarray de shape (N, 2) contenant les points image.

        Returns:
            np.ndarray de shape (N, 2) en mètres, ou None si pas de transformation.
        """
        if not self.transform_computed:
            return None

        N = points.shape[0]
        ones = np.ones((N, 1), dtype=points.dtype)
        pts = np.hstack([points, ones])  # (N, 3)

        if self.transform_type == "homography" and self.homography_matrix is not None:
            world_pts = (self.homography_matrix @ pts.T).T  # (N, 3)
            world_pts = world_pts[:, :2] / world_pts[:, 2:3]
        elif self.transform_type == "affine" and self.affine_matrix is not None:
            world_pts = (self.affine_matrix @ pts.T).T  # (N, 2)
        else:
            return None

        return world_pts / 1000.0

    @timer
    def _init_arena_plot(self, arena_size_mm=(3000, 2000)):
        import matplotlib as mpl

        mpl.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import patches
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

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
        arrow_len_mm=300.0,
        window_name="Arena",
    ):
        import matplotlib.lines as mlines
        import matplotlib.pyplot as plt
        import matplotlib.transforms as mtransforms
        from matplotlib import patches

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

        crate_ids = {blue_crate_id, yellow_crate_id, empty_crate_id}
        crate_colors = {
            blue_crate_id: "#1E90FF",
            yellow_crate_id: "#FFD700",
            empty_crate_id: "#222222",
        }

        starting_zone_blue = patches.Rectangle(
            (
                arena_elements["starting_zone"]["blue"]["position"][0] * 1000,
                arena_elements["starting_zone"]["blue"]["position"][1] * 1000,
            ),
            arena_elements["starting_zone"]["blue"]["width"] * 1000,
            arena_elements["starting_zone"]["blue"]["height"] * 1000,
            linewidth=1.5,
            edgecolor="k",
            facecolor=arena_elements["starting_zone"]["blue"]["color"],
            alpha=0.30,
        )
        self._arena_ax.add_patch(starting_zone_blue)
        starting_zone_yellow = patches.Rectangle(
            (
                arena_elements["starting_zone"]["yellow"]["position"][0] * 1000,
                arena_elements["starting_zone"]["yellow"]["position"][1] * 1000,
            ),
            arena_elements["starting_zone"]["yellow"]["width"] * 1000,
            arena_elements["starting_zone"]["yellow"]["height"] * 1000,
            linewidth=1.5,
            edgecolor="k",
            facecolor=arena_elements["starting_zone"]["yellow"]["color"],
            alpha=0.30,
        )
        self._arena_ax.add_patch(starting_zone_yellow)
        grenier_zone = patches.Rectangle(
            (600, 0),
            1800,
            400,
            linewidth=1.5,
            edgecolor="k",
            facecolor="#34281A",
            alpha=0.30,
        )
        self._arena_ax.add_patch(grenier_zone)
        starting_zone_ninja_blue = patches.Rectangle(
            (600, 0),
            200,
            200,
            linewidth=1.5,
            edgecolor="k",
            facecolor=crate_colors[blue_crate_id],
            alpha=0.30,
        )
        self._arena_ax.add_patch(starting_zone_ninja_blue)
        starting_zone_ninja_yellow = patches.Rectangle(
            (2200, 0),
            200,
            200,
            linewidth=1.5,
            edgecolor="k",
            facecolor=crate_colors[yellow_crate_id],
            alpha=0.30,
        )
        self._arena_ax.add_patch(starting_zone_ninja_yellow)

        # zone de depot
        for zone in arena_elements["zone_depot"]:
            depot_zone = patches.Rectangle(
                (zone["position"][0] * 1000, zone["position"][1] * 1000),
                zone["width"] * 1000,
                zone["height"] * 1000,
                linewidth=1.5,
                edgecolor="k",
                facecolor=zone["color"],
                alpha=0.30,
            )
            self._arena_ax.add_patch(depot_zone)

            self._arena_ax.text(
                zone["position"][0] * 1000 + zone["width"] * 1000 / 2,
                zone["position"][1] * 1000 + zone["height"] * 1000 / 2,
                f"{zone['id_zone']}",
                fontsize=15,
                color="black",
                ha="center",
                va="center",
            )

        for zone in arena_elements["zone_ramassage"]:
            zone_ramassage = patches.Rectangle(
                (zone["position"][0] * 1000, zone["position"][1] * 1000),
                zone["width"] * 1000,
                zone["height"] * 1000,
                linewidth=1.5,
                edgecolor="k",
                facecolor=zone["color"],
                alpha=0.30,
            )
            self._arena_ax.add_patch(zone_ramassage)

            self._arena_ax.text(
                zone["position"][0] * 1000 + zone["width"] * 1000 / 2,
                zone["position"][1] * 1000 + zone["height"] * 1000 / 2,
                f"{zone['id_zone']}",
                fontsize=15,
                color="black",
                ha="center",
                va="center",
            )

        CRATE_W, CRATE_H = 150.0, 50.0  # mm (vue du dessus)
        ARUCO_SIZE = 40.0  # mm

        for idx, (mid, pos_m, yaw) in enumerate(detected_world):
            if mid in self.ref_markers_world:
                color = "black"
                edgecolor = "white"
                alpha = 1
            else:
                if mid in blue_team_ids or mid in blue_reserve_ids:
                    color = crate_colors[blue_crate_id]
                elif mid in yellow_team_ids or mid in yellow_reserve_ids:
                    color = crate_colors[yellow_crate_id]
                else:
                    color = cmap(idx % 10)
                edgecolor = "k"
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

            if mid in crate_ids:
                # Dessiner la caisse comme un rectangle réaliste
                crate_color = crate_colors[mid]
                transform = (
                    mtransforms.Affine2D().rotate_around(x_mm, y_mm, yaw)
                    + self._arena_ax.transData
                )

                # Rectangle extérieur (la caisse)
                crate_rect = patches.Rectangle(
                    (x_mm - CRATE_W / 2, y_mm - CRATE_H / 2),
                    CRATE_W,
                    CRATE_H,
                    linewidth=1.5,
                    edgecolor="k",
                    facecolor=crate_color,
                    alpha=0.85,
                    transform=transform,
                )
                self._arena_ax.add_patch(crate_rect)

                # Carré blanc au centre (fond de l'ArUco)
                aruco_bg = patches.Rectangle(
                    (x_mm - ARUCO_SIZE / 2, y_mm - ARUCO_SIZE / 2),
                    ARUCO_SIZE,
                    ARUCO_SIZE,
                    linewidth=0,
                    facecolor="white",
                    transform=transform,
                )
                self._arena_ax.add_patch(aruco_bg)

                # Motif noir au centre (tag ArUco simplifié)
                inner = ARUCO_SIZE * 0.6
                aruco_fg = patches.Rectangle(
                    (x_mm - inner / 2, y_mm - inner / 2),
                    inner,
                    inner,
                    linewidth=0,
                    facecolor="black",
                    transform=transform,
                )
                self._arena_ax.add_patch(aruco_fg)
            else:
                # Marqueurs génériques : carré 120mm
                s = 100.0
                lower_left = (x_mm - s / 2.0, y_mm - s / 2.0)
                square = patches.Rectangle(
                    lower_left,
                    s,
                    s,
                    linewidth=1,
                    edgecolor=edgecolor,
                    facecolor=color,
                    alpha=alpha,
                )
                self._arena_ax.add_patch(square)

            dx = math.cos(yaw) * arrow_len_mm
            dy = math.sin(yaw) * arrow_len_mm
            if mid not in crate_ids and mid not in self.ref_markers_world:
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
            if mid not in crate_ids:
                self._arena_ax.text(
                    x_mm + s / 2 + 6,
                    y_mm - s / 2 - 3,
                    f"{mid}: {name}\n({x_mm:.0f}, {y_mm:.0f})",
                    fontsize=9,
                    color="black",
                    verticalalignment="bottom",
                )
            else:
                self._arena_ax.text(
                    x_mm + s / 2 + 6,
                    y_mm - s / 4,
                    f"({x_mm:.0f}, {y_mm:.0f})",
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

    def _detect_single_tile(self, gray, ox, oy, tile_w, tile_h):
        """Détecte les marqueurs sur une tuile upscalée (appelé en thread).

        Returns:
            Liste de (corners_reprojected, id_array) pour chaque marqueur trouvé.
        """
        tile = gray[oy : oy + tile_h, ox : ox + tile_w]
        # Upscale 2x sur GPU si disponible, sinon CPU
        if self.use_cuda:
            gpu_tile = cv2.cuda_GpuMat()
            gpu_tile.upload(tile)
            gpu_up = cv2.cuda.resize(gpu_tile, (tile_w * 2, tile_h * 2))
            tile_up = gpu_up.download()
        else:
            tile_up = cv2.resize(
                tile,
                None,
                fx=2.0,
                fy=2.0,
                interpolation=cv2.INTER_LINEAR,
            )
        t_corners, t_ids, _ = cv2.aruco.detectMarkers(
            tile_up,
            self.aruco_dict,
            parameters=self.aruco_params,
        )
        results = []
        if t_ids is not None:
            for i, mid_arr in enumerate(t_ids):
                # Re-projeter : ÷2 (upscale) + offset tuile
                original_corners = t_corners[i] / 2.0
                original_corners[:, :, 0] += ox
                original_corners[:, :, 1] += oy
                results.append((original_corners, mid_arr))
        return results

    def _detect_multiscale(self, gray):
        """Détection multi-échelle : full-frame + tuiles 2x2 en parallèle.

        Returns:
            (corners, ids, rejected) au format cv2.aruco.detectMarkers.
        """
        # Passe 1 : détection sur image complète
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray,
            self.aruco_dict,
            parameters=self.aruco_params,
        )

        num_found = 0 if ids is None else len(ids)

        # Passe 2 : tuiles en parallèle si pas assez de marqueurs détectés
        if num_found < self.multiscale_min_markers:
            h, w = gray.shape[:2]
            overlap = 100
            tile_w = w // 2 + overlap
            tile_h = h // 2 + overlap

            tile_offsets = [
                (0, 0),
                (w - tile_w, 0),
                (0, h - tile_h),
                (w - tile_w, h - tile_h),
            ]

            found_ids = set() if ids is None else {int(i[0]) for i in ids}
            all_corners = list(corners) if corners is not None else []
            all_ids = list(ids) if ids is not None else []

            # Lancer les 4 tuiles en parallèle
            futures = [
                self._tile_pool.submit(
                    self._detect_single_tile,
                    gray,
                    ox,
                    oy,
                    tile_w,
                    tile_h,
                )
                for ox, oy in tile_offsets
            ]

            for future in futures:
                for original_corners, mid_arr in future.result():
                    mid = int(mid_arr[0])
                    if mid not in found_ids:
                        all_corners.append(original_corners)
                        all_ids.append(mid_arr)
                        found_ids.add(mid)

            if all_ids:
                corners = tuple(all_corners)
                ids = np.array(all_ids)
            else:
                corners, ids = (), None

        return corners, ids, rejected

    @timer
    def analyze_frame(
        self, frame, show_arena=True, arena_window_name="Arena", show_video=True
    ):
        # Preprocessing GPU si disponible, sinon CPU
        if self.use_cuda:
            self._gpu_mat.upload(frame)
            if frame.ndim == 3:
                gpu_gray = cv2.cuda.cvtColor(self._gpu_mat, cv2.COLOR_BGR2GRAY)
            else:
                gpu_gray = self._gpu_mat
            gpu_gray = self.clahe_cuda.apply(gpu_gray, cv2.cuda.Stream.Null())
            gray = gpu_gray.download()
        else:
            gray = (
                frame
                if frame.ndim == 2
                else cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY,
                )
            )
            gray = self.clahe.apply(gray)

        # Détection ArUco (multi-échelle si activée)
        if self.multiscale_enabled:
            corners, ids, _ = self._detect_multiscale(gray)
        else:
            corners, ids, _ = cv2.aruco.detectMarkers(
                gray,
                self.aruco_dict,
                parameters=self.aruco_params,
            )

        if ids is None:
            if show_arena:
                self.update_arena_display(
                    detected_world=[],
                    window_name=arena_window_name,
                )
            return (frame if show_video else None), []

        # Dessiner les marqueurs détectés seulement si affichage activé
        if show_video:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        self.compute_transform_from_refs(corners, ids, use_cache=True)

        detected_world = []

        if self.transform_computed:
            # Pré-calcul des constantes
            pi = math.pi
            half_pi = pi / 2.0
            two_pi = 2.0 * pi

            num_markers = len(ids)

            # Collecte de tous les points à transformer en un seul batch
            # Pour chaque marqueur : centre, corner0, corner1 = 3 points
            all_points = np.empty((num_markers * 3, 2), dtype=np.float32)
            for i in range(num_markers):
                center_img = corners[i][0].mean(axis=0)
                all_points[i * 3] = center_img
                all_points[i * 3 + 1] = corners[i][0][0]
                all_points[i * 3 + 2] = corners[i][0][1]

            # Transformation batch : une seule multiplication matricielle
            all_world = self.transform_points_to_world_batch(all_points)

            if all_world is not None:
                # Pré-calcul du cache indicator pour les annotations vidéo
                if show_video:
                    visible_refs = [
                        int(ids[j][0])
                        for j in range(num_markers)
                        if int(ids[j][0]) in self.ref_markers_world
                    ]
                    use_cache_indicator = len(visible_refs) < 3

                for i in range(num_markers):
                    mid = int(ids[i][0])
                    pos_world = all_world[i * 3]
                    corner0_world = all_world[i * 3 + 1]
                    corner1_world = all_world[i * 3 + 2]

                    # Calcul du yaw
                    vec_world = corner1_world - corner0_world
                    yaw = math.atan2(vec_world[1], vec_world[0]) + half_pi
                    yaw = ((yaw + pi) % two_pi) - pi

                    detected_world.append((mid, pos_world, yaw))

                    # Annotations vidéo seulement si affichage activé
                    if show_video:
                        cache_indicator = ""
                        if use_cache_indicator and mid in self.ref_markers_world:
                            cache_indicator = " (cache)"

                        self._annotate_marker(
                            frame,
                            all_points[i * 3],
                            mid,
                            pos_world,
                            yaw,
                            ids,
                            cache_indicator,
                        )
        else:
            # Si pas de transformation calculée, annotations seulement si affichage activé
            if show_video:
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

        # Lissage temporel : carry-forward des marqueurs statiques manqués
        current_time = time.time()
        detected_ids = {mid for mid, _, _ in detected_world}

        # Mettre à jour l'historique avec les marqueurs détectés
        for mid, pos, yaw in detected_world:
            if mid not in self._no_carry_ids:
                self.marker_history[mid] = (pos, yaw, current_time, 0)

        # Carry-forward des marqueurs manqués (statiques uniquement)
        expired = []
        for mid, (pos, yaw, _, misses) in self.marker_history.items():
            if mid in detected_ids:
                continue
            misses += 1
            if misses <= self.marker_carry_frames:
                self.marker_history[mid] = (pos, yaw, current_time, misses)
                detected_world.append((mid, pos, yaw))
            else:
                expired.append(mid)
        for mid in expired:
            del self.marker_history[mid]

        if show_arena:
            try:
                self.update_arena_display(
                    detected_world=detected_world, window_name=arena_window_name
                )
            except Exception:
                pass

        return (frame if show_video else None), detected_world
