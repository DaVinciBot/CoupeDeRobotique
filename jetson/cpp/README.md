# Arena Vision (C++17)

Localisation de marqueurs ArUco vue du dessus pour l'arène de la Coupe de Robotique,
sur Jetson Orin Nano avec caméra CSI IMX219. Réécriture C++17 du système Python
(`../python/`) visant **≥ 15 fps de bout en bout**.

Pipeline : **capture GStreamer NVMM → niveaux de gris/resize GPU → détection ArUco →
homographie de référence → coordonnées arène → envoi LoRa**.

---

## Dépendances

> ⚠️ **À installer soi-même.** Le `cmake` du projet ne fait que *localiser* les
> bibliothèques déjà installées (`find_package`) — il n'installe **rien**.

Résumé de ce qu'il faut :

- **CMake ≥ 3.18** + compilateur C++17 (`build-essential`).
- **OpenCV 4.x compilé AVEC** le module contrib **`aruco`** (obligatoire) et,
  pour le pré-traitement GPU, les modules **CUDA** `cudaimgproc` + `cudawarping`
  (optionnel — sans eux, repli automatique sur le CPU).
- **GStreamer** (présent dans JetPack) pour la capture `nvarguscamerasrc`.
- **`termios` POSIX** (libc) pour le port série LoRa — aucune dépendance externe.

Aucun sous-module git requis (ArUco est dans OpenCV).

### 1. Outils de base + GStreamer

```bash
sudo apt update
sudo apt install -y build-essential cmake git pkg-config \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-tools
```

### 2. OpenCV — choisir UNE des deux options

#### Option A — paquet apt (rapide, **CPU uniquement**, sans CUDA)

L'OpenCV d'Ubuntu inclut le module `aruco` mais **pas** CUDA. Le programme
fonctionne (repli CPU automatique pour le pré-traitement), mais sans accélération GPU.

```bash
sudo apt install -y libopencv-dev
```

#### Option B — compilation depuis les sources avec CUDA (recommandé pour la perf)

⚠️ Long sur Orin Nano (~1–2 h). Prévoir de la swap si la RAM est juste
(`sudo fallocate -l 8G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`).

```bash
# Dépendances de build d'OpenCV
sudo apt install -y libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev \
  libv4l-dev libxvidcore-dev libx264-dev libjpeg-dev libpng-dev libtiff-dev \
  libtbb-dev libatlas-base-dev gfortran

# Sources (même version pour opencv et opencv_contrib)
cd ~
git clone --depth 1 -b 4.10.0 https://github.com/opencv/opencv.git
git clone --depth 1 -b 4.10.0 https://github.com/opencv/opencv_contrib.git

cd ~/opencv && mkdir -p build && cd build
cmake -D CMAKE_BUILD_TYPE=Release \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D WITH_CUDA=ON \
      -D CUDA_ARCH_BIN=8.7 \
      -D ENABLE_FAST_MATH=ON \
      -D CUDA_FAST_MATH=ON \
      -D WITH_CUBLAS=ON \
      -D WITH_GSTREAMER=ON \
      -D WITH_LIBV4L=ON \
      -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
      -D BUILD_opencv_python3=OFF \
      -D BUILD_EXAMPLES=OFF -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF ..

make -j$(nproc)
sudo make install
sudo ldconfig
```

> `CUDA_ARCH_BIN=8.7` correspond au GPU Ampere de l'Orin Nano.
> Remplacer `4.10.0` par la version OpenCV souhaitée (compatible avec le CUDA de votre JetPack).

Vérifier l'installation : `pkg-config --modversion opencv4` (ou regarder le message
`OpenCV CUDA ... found` affiché par le `cmake` du projet).

---

## Compilation

```bash
cd jetson/cpp
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
```

Produit l'exécutable `./arena_vision`.

---

## Lancement

```bash
# depuis jetson/cpp
cp .env.example .env          # éditer si besoin
set -a; source .env; set +a
./build/arena_vision
```

### Test sans matériel

```bash
# Logique / protocole seuls (sans caméra ni UART) :
DUMMY_DETECTION=1 DUMMY_LORA=1 DEBUG_MODE=1 ./build/arena_vision

# Détection depuis une image ou une vidéo, paquets affichés :
INPUT_FILE=arena.png DUMMY_LORA=1 DEBUG_MODE=1 ./build/arena_vision
```

Arrêt propre : `Ctrl+C` (SIGINT).

---

## Paramètres (variables d'environnement, voir `.env.example`)

| Variable | Défaut | Description |
|----------|--------|-------------|
| `CAMERA_ID` | 0 | Port CSI (0 = CAM0, 1 = CAM1) |
| `SENSOR_WIDTH` / `SENSOR_HEIGHT` / `SENSOR_FPS` | 3280 / 2464 / 21 | Mode de capture (max IMX219) |
| `DETECT_DOWNSCALE` | 1.0 | Réduction GPU avant détection ; n'augmenter que si la détection est trop lente |
| `NUM_THREADS` | 6 | Nombre de threads OpenCV/ArUco (= cœurs de l'Orin Nano) |
| `DETECT_PARALLEL` | off | `off` / `tile` (4 tuiles parallèles) / `frame` (N threads round-robin) |
| `ROBOT_MARKER_ID` / `ENEMY_MARKER_ID` | 6 / 1 | Robots suivis (allié / ennemi) |
| `BLUE_CRATE_MARKER_ID` / `YELLOW_CRATE_MARKER_ID` / `EMPTY_CRATE_MARKER_ID` | 36 / 47 / 41 | Caisses bleue / jaune / vide |
| `ZONE_TOLERANCE_CM` | 5.0 | Tolérance d'appartenance d'une caisse à une zone |
| `LORA_PORT` / `LORA_BAUD` | /dev/ttyTHS1 / 115200 | Port UART LoRa |
| `CALIBRATION_FILE` | — | Fichier OpenCV `.yml` (`camera_matrix`, `dist_coeffs`) ; active l'undistort GPU |
| `DUMMY_LORA` | false | Affiche les paquets au lieu d'écrire sur l'UART |
| `DUMMY_DETECTION` | false | Monde synthétique (sans caméra) pour tester la FSM et le protocole |
| `INPUT_FILE` | — | Image/vidéo au lieu de la caméra CSI |
| `DEBUG_MODE` | false | JSON par frame + FPS sur la sortie standard |

---

## Protocole LoRa

Trames texte, champs séparés par `|`, terminées par `\n`, à 115200 baud.

| Cmd | Sens | Description |
|-----|------|-------------|
| **1** | PAMI → Jetson | Demande d'ID → le Jetson répond **cmd 2** `2\|<pid>` |
| **4** | Robot → Jetson | `4\|<B\|Y>` → démarre le match |
| **3** | Jetson → PAMI | Une fois à T+90 s : `3\|id\|x\|y\|...` (attribution des dépôts) |
| **5** | Jetson → Robot/PAMI | En continu pendant le match : **paquet vision 137 entiers** |

**Paquet cmd 5 (137 entiers)** : `9` entiers d'en-tête
`[rx, ry, rθ, ex, ey, eθ, 0, 0, vitesse_ennemi]` puis `32` caisses ×
`[id_zone, x_enc, y_enc, id_couleur]`, complété par des `(0,0,0,0)` jusqu'à 32.
Encodage : position/vitesse = `round(valeur × 1000)`, angle = `round(rad × 1000)`,
couleur `36→0 / 47→1 / 41→2`. (C'est le format réellement attendu par les robots ;
le format à tokens R/Z/U de l'ancien `lora_protocol.md` est une doc obsolète.)

> Libérer `/dev/ttyTHS1` au besoin : `sudo systemctl disable --now nvgetty`.
