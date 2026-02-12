# Jetson - Détection ArUco

## ⚠️ Installation OpenCV

**N'installez surtout pas opencv avec pip !** La version build sur pip ne contient pas CUDA (essentiel pour le bon fonctionnement sur Jetson).

À la place, il faut build et installer OpenCV depuis le code source directement sur la Jetson avec le module CUDA **et GStreamer** (il y a plein de repo GitHub qui le font) (et oui ça prend 4h à compiler).

**Installez OpenCV 4.5.1** pour avoir la meilleure compatibilité avec le code !

### Compilation avec GStreamer (pour caméras CSI)

Lors de la compilation d'OpenCV, assurez-vous d'activer GStreamer :

```bash
cmake -D WITH_GSTREAMER=ON \
      -D WITH_CUDA=ON \
      -D CUDA_ARCH_BIN="5.3,6.2,7.2" \
      ...
```

## 🎥 Support Caméra

Ce projet supporte deux types de caméras :

### 1. Caméra USB (Webcam)
Configuration par défaut, fonctionne avec n'importe quelle webcam USB.

```bash
# Dans .env
USE_CSI_CAMERA=False
CAMERA_ID=0
FPS=15
```

### 2. Caméra CSI IMX219 (Raspberry Pi Camera V2)
Optimisé pour les caméras CSI sur Jetson avec accélération matérielle.

```bash
# Dans .env
USE_CSI_CAMERA=True
CAMERA_ID=0  # 0 pour CAM0, 1 pour CAM1
FPS=30
```

**📖 Guide complet:** Voir [CSI_CAMERA_SETUP.md](./CSI_CAMERA_SETUP.md)

**🔧 Test de compatibilité:**
```bash
python3 test_csi_camera.py
```

## Installation et Configuration

1. Copier le fichier d'exemple :
```bash
cp .env.example .env
```

2. Éditer `.env` selon votre configuration

3. Installer les dépendances Python :
```bash
pip3 install -r requirements.txt
```

4. Lancer l'application :
```bash
python3 main.py
```

## Mode Calibration

Pour calibrer votre caméra avec un damier :

```bash
# Dans .env
CALIBRATE_MODE=True
```

Puis lancez `python3 main.py` et suivez les instructions.
