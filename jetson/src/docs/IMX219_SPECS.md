# Spécifications IMX219 (Raspberry Pi Camera Module V2)

## Caractéristiques du capteur

- **Modèle**: Sony IMX219PQ
- **Type**: CMOS
- **Résolution**: 8 mégapixels (3280 x 2464 pixels)
- **Taille du capteur**: 1/4" (3.68mm x 2.76mm)
- **Taille du pixel**: 1.12 μm x 1.12 μm
- **Interface**: MIPI CSI-2

## Modes vidéo supportés

| Mode | Résolution | FPS Max | Binning | FOV | Notes |
|------|-----------|---------|---------|-----|-------|
| 1 | 3280x2464 | 21 | 1x1 | Complet | Photo haute qualité |
| 2 | 1920x1080 | 30 | 2x2 | Complet | **Recommandé** - Vidéo Full HD |
| 3 | 1640x1232 | 40 | 2x2 | Complet | Compromis résolution/FPS |
| 4 | 1280x720 | 60 | 2x2 + crop | Réduit | Haute fréquence |
| 5 | 640x480 | 90 | 2x2 + crop | Réduit | Très haute fréquence |

## Optique standard

- **Distance focale**: 3.04 mm
- **Ouverture**: f/2.0
- **Champ de vision (FOV)**:
  - Horizontal: 62.2°
  - Vertical: 48.8°
  - Diagonal: 75°

## Performances sur Jetson Nano

### Mode 1920x1080 @ 30 FPS (Recommandé)

**Avantages:**
- ✅ Latence minimale (~30ms)
- ✅ Utilisation NVMM (mémoire partagée GPU)
- ✅ Conversion matérielle (nvvidconv)
- ✅ Excellent compromis résolution/performance

**Utilisation des ressources:**
- CPU: ~15-20%
- GPU: ~30-40%
- RAM: ~500 MB
- Bande passante: ~60 MB/s

### Mode 3280x2464 @ 21 FPS (Haute résolution)

**Avantages:**
- ✅ Résolution maximale
- ✅ Détection de petits marqueurs
- ✅ Meilleure précision de position

**Inconvénients:**
- ❌ FPS limité (21 max)
- ❌ Charge CPU/GPU élevée
- ❌ Latence accrue (~50ms)

**Utilisation des ressources:**
- CPU: ~25-35%
- GPU: ~60-70%
- RAM: ~800 MB
- Bande passante: ~150 MB/s

### Mode 1280x720 @ 60 FPS (Haute fréquence)

**Avantages:**
- ✅ Très faible latence (~15ms)
- ✅ Fluidité maximale
- ✅ Idéal pour suivi rapide

**Inconvénients:**
- ❌ Résolution réduite
- ❌ FOV légèrement réduit (crop)
- ❌ Détection limitée pour petits marqueurs

**Utilisation des ressources:**
- CPU: ~20-25%
- GPU: ~35-45%
- RAM: ~400 MB
- Bande passante: ~55 MB/s

## Configuration GStreamer optimale

### Pour 1920x1080 @ 30 FPS

```bash
nvarguscamerasrc sensor-id=0 ! \
  video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=30/1 ! \
  nvvidconv flip-method=0 ! \
  video/x-raw, width=1920, height=1080, format=BGRx ! \
  videoconvert ! \
  video/x-raw, format=BGR ! \
  appsink
```

### Pour 3280x2464 @ 21 FPS (Haute résolution)

```bash
nvarguscamerasrc sensor-id=0 ! \
  video/x-raw(memory:NVMM), width=3280, height=2464, format=NV12, framerate=21/1 ! \
  nvvidconv flip-method=0 ! \
  video/x-raw, width=3280, height=2464, format=BGRx ! \
  videoconvert ! \
  video/x-raw, format=BGR ! \
  appsink
```

### Pour 1280x720 @ 60 FPS (Haute fréquence)

```bash
nvarguscamerasrc sensor-id=0 ! \
  video/x-raw(memory:NVMM), width=1280, height=720, format=NV12, framerate=60/1 ! \
  nvvidconv flip-method=0 ! \
  video/x-raw, width=1280, height=720, format=BGRx ! \
  videoconvert ! \
  video/x-raw, format=BGR ! \
  appsink
```

## Paramètres nvarguscamerasrc avancés

| Paramètre | Valeurs | Description |
|-----------|---------|-------------|
| sensor-id | 0 ou 1 | Port CSI (0=CAM0, 1=CAM1) |
| sensor-mode | 0-4 | Mode capteur (auto=0) |
| exposuretimerange | "min max" | Temps d'exposition (ns) |
| gainrange | "min max" | Gain ISO (1.0 - 16.0) |
| wbmode | 0-9 | Balance des blancs |
| aeantibanding | 0-3 | Anti-scintillement |

### Exemple avec contrôle manuel

```bash
nvarguscamerasrc sensor-id=0 \
  exposuretimerange="10000000 30000000" \
  gainrange="1 8" \
  wbmode=1 \
  aeantibanding=1 ! \
  video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=30/1 ! \
  ...
```

## Flip methods (rotation de l'image)

| Valeur | Transformation |
|--------|----------------|
| 0 | Aucune |
| 1 | Rotation 90° horaire |
| 2 | Rotation 180° |
| 3 | Rotation 90° anti-horaire |
| 4 | Miroir horizontal |
| 5 | Miroir vertical |
| 6 | Miroir horizontal + rotation 90° horaire |
| 7 | Miroir horizontal + rotation 90° anti-horaire |

## Comparaison USB vs CSI

| Aspect | USB Webcam | CSI IMX219 |
|--------|------------|------------|
| **Résolution max** | 1920x1080 | 3280x2464 |
| **FPS @ 1080p** | 15-30 | 30 |
| **Latence** | 80-150ms | 20-40ms |
| **CPU Usage** | Élevé (30-40%) | Faible (15-20%) |
| **GPU Usage** | Minimal (<10%) | Moyen (30-40%) |
| **Bande passante** | USB 2.0/3.0 | MIPI CSI-2 |
| **Accélération HW** | Non | Oui (NVMM) |
| **Qualité image** | Variable | Excellente |
| **Prix** | 20-100€ | 20-30€ |

## Recommandations par cas d'usage

### Coupe de Robotique (détection ArUco)

**Configuration recommandée:**
```bash
CAMERA_WIDTH=1920
CAMERA_HEIGHT=1080
FPS=30
USE_CSI_CAMERA=True
```

**Raison:** Bon compromis entre résolution (détection de marqueurs) et FPS (réactivité).

### Suivi d'objet haute vitesse

**Configuration recommandée:**
```bash
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
FPS=60
USE_CSI_CAMERA=True
```

**Raison:** Latence minimale et haute fréquence d'échantillonnage.

### Cartographie/Localisation précise

**Configuration recommandée:**
```bash
CAMERA_WIDTH=3280
CAMERA_HEIGHT=2464
FPS=21
USE_CSI_CAMERA=True
```

**Raison:** Résolution maximale pour précision de détection.

## Calibration

Pour une calibration précise de l'IMX219 :

1. Utiliser un damier de calibration avec carrés de 2-3 cm
2. Capturer 50-100 images sous différents angles
3. Couvrir tout le champ de vision
4. Varier les distances (30cm à 2m)
5. Assurer un bon éclairage uniforme

## Liens utiles

- [Sony IMX219 Datasheet](https://www.sony-semicon.co.jp/products/common/pdf/IMX219PQ_ProductBrief.pdf)
- [Raspberry Pi Camera Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [NVIDIA Jetson Camera Documentation](https://developer.nvidia.com/embedded/learn/tutorials/first-picture-csi-usb-camera)
- [GStreamer Documentation](https://gstreamer.freedesktop.org/documentation/)
