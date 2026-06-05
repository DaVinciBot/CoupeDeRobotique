# Configuration Caméra CSI IMX219 sur Jetson

## Introduction

Ce guide explique comment configurer et utiliser une caméra CSI (Camera Serial Interface) IMX219 avec le système de détection ArUco.

## Prérequis

### Matériel
- Jetson Nano, Xavier NX, AGX Xavier, ou autre carte Jetson
- Caméra CSI IMX219 (Raspberry Pi Camera Module V2 ou équivalent)
- Câble plat CSI connecté au port CAM0 ou CAM1 de la Jetson

### Logiciel
- JetPack SDK installé (inclut les pilotes CSI)
- OpenCV compilé avec support GStreamer
- Python 3.8+

## Vérification du support GStreamer

Pour vérifier que votre OpenCV supporte GStreamer :

```bash
python3 -c "import cv2; print(cv2.getBuildInformation())" | grep -i gstreamer
```

Vous devriez voir :
```
GStreamer:                   YES (1.14.5)
```

Si GStreamer n'est pas supporté, vous devrez recompiler OpenCV avec le support GStreamer activé.

## Test de la caméra CSI

### 1. Test avec gst-launch (sans Python)

```bash
# Test simple de capture
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! \
    'video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=30/1' ! \
    nvvidconv ! 'video/x-raw, format=BGRx' ! \
    videoconvert ! 'video/x-raw, format=BGR' ! \
    fakesink
```

Si cette commande fonctionne sans erreur, votre caméra CSI est correctement configurée.

### 2. Test avec OpenCV

```python
import cv2

# Pipeline GStreamer pour IMX219
gst_pipeline = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM), width=1920, height=1080, "
    "format=NV12, framerate=30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw, width=1920, height=1080, format=BGRx ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! "
    "appsink"
)

cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print(f"✅ Caméra CSI fonctionne ! Résolution: {frame.shape}")
    else:
        print("❌ Impossible de lire une frame")
else:
    print("❌ Impossible d'ouvrir la caméra CSI")

cap.release()
```

## Configuration pour l'application de détection ArUco

### 1. Fichier .env

Créez ou modifiez votre fichier `.env` :

```bash
# Activer le mode CSI
USE_CSI_CAMERA=True

# ID de la caméra (0 pour CAM0, 1 pour CAM1)
CAMERA_ID=0

# FPS (30 recommandé pour IMX219)
FPS=30

# Résolution (IMX219 supporte jusqu'à 3280x2464, mais 1920x1080 est recommandé)
CAMERA_WIDTH=1920
CAMERA_HEIGHT=1080

# Les autres paramètres restent identiques
USE_THREADED_CAMERA=True
SHOW_CAMERA_FEED=True
SHOW_ARENA=True
```

### 2. Lancement de l'application

```bash
cd /Users/clement/Documents/CoupeDeRobotique/jetson
python3 main.py
```

## Paramètres de la pipeline GStreamer

La pipeline GStreamer utilisée dans le code :

```
nvarguscamerasrc sensor-id={camera_id} ! 
video/x-raw(memory:NVMM), width={width}, height={height}, format=NV12, framerate={fps}/1 ! 
nvvidconv flip-method=0 ! 
video/x-raw, width={width}, height={height}, format=BGRx ! 
videoconvert ! 
video/x-raw, format=BGR ! 
appsink
```

### Explication des composants :

- **nvarguscamerasrc** : Source de capture pour caméras CSI sur Jetson
- **sensor-id** : ID du port CSI (0 ou 1)
- **video/x-raw(memory:NVMM)** : Utilise la mémoire partagée NVMM (accélération matérielle)
- **nvvidconv** : Convertisseur vidéo accéléré par GPU
- **flip-method** : Rotation de l'image (0=aucune, 2=rotation 180°, etc.)
- **videoconvert** : Conversion de format final
- **appsink** : Permet à l'application de recevoir les frames

## Résolutions supportées par IMX219

| Résolution | FPS Max | Usage recommandé |
|------------|---------|------------------|
| 3280x2464  | 21      | Photos haute qualité |
| 1920x1080  | 30      | **Recommandé** - Bon compromis |
| 1280x720   | 60      | Haute fréquence |
| 640x480    | 90      | Très haute fréquence |

## Rotation de l'image

Si votre caméra est montée dans une orientation différente, modifiez le paramètre `flip-method` dans `camera.py` :

- **0** : Pas de rotation
- **1** : Rotation 90° horaire
- **2** : Rotation 180°
- **3** : Rotation 90° anti-horaire
- **4** : Miroir horizontal
- **5** : Miroir vertical

## Dépannage

### Problème : "No cameras available"

**Solutions :**
1. Vérifier que le câble CSI est bien connecté
2. Redémarrer la Jetson
3. Vérifier avec : `ls /dev/video*` (devrait montrer /dev/video0)
4. Tester avec : `nvgstcapture-1.0`

### Problème : "GStreamer pipeline failed"

**Solutions :**
1. Vérifier le support GStreamer dans OpenCV
2. Installer les paquets manquants :
   ```bash
   sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-good gstreamer1.0-plugins-bad
   ```

### Problème : "nvarguscamerasrc not found"

**Solutions :**
1. Vous n'êtes probablement pas sur une Jetson ou JetPack n'est pas installé
2. Installer JetPack SDK complet
3. Utiliser une caméra USB classique avec `USE_CSI_CAMERA=False`

### Problème : Faible FPS ou images saccadées

**Solutions :**
1. Réduire la résolution (essayer 1280x720)
2. Vérifier que `USE_THREADED_CAMERA=True`
3. Augmenter la puissance de la Jetson (mode performance) :
   ```bash
   sudo nvpmodel -m 0
   sudo jetson_clocks
   ```

## Fallback automatique

Le code inclut un fallback automatique : si la caméra CSI ne peut pas être ouverte, le système essaiera automatiquement d'utiliser V4L2 (caméra USB). Un message d'avertissement sera affiché :

```
⚠️  Échec ouverture caméra CSI, tentative avec V4L2...
```

## Performance

### Avantages de la caméra CSI sur Jetson :
- ✅ Accès direct à la mémoire NVMM (pas de copie CPU)
- ✅ Conversion de format accélérée par GPU (nvvidconv)
- ✅ Latence réduite
- ✅ Meilleure utilisation de la bande passante

### Comparaison USB vs CSI :
| Aspect | USB Webcam | CSI IMX219 |
|--------|------------|------------|
| FPS @ 1080p | 15-30 | 30 |
| Latence | ~100ms | ~30ms |
| CPU Usage | Élevé | Faible |
| GPU Usage | Minimal | Moyen |

## Calibration de la caméra CSI

Pour calibrer votre caméra CSI IMX219 :

```bash
# Dans le fichier .env
CALIBRATE_MODE=True
USE_CSI_CAMERA=True
FPS=30
NUM_CALIB_IMAGES=50

# Lancer la calibration
python3 main.py
```

Suivez les instructions à l'écran pour capturer les images du damier avec différentes orientations.

## Ressources supplémentaires

- [Documentation NVIDIA Jetson](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)
- [GStreamer sur Jetson](https://developer.ridgerun.com/wiki/index.php?title=Jetson_Nano/Gstreamer)
- [IMX219 Datasheet](https://www.sony-semicon.co.jp/products/common/pdf/IMX219PQ_ProductBrief.pdf)
