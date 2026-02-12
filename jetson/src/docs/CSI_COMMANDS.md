# Commandes utiles pour caméra CSI sur Jetson

## Diagnostic de base

### Vérifier les périphériques vidéo
```bash
ls -la /dev/video*
```

### Informations sur la caméra avec v4l2
```bash
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats-ext
```

### Vérifier GStreamer
```bash
# Vérifier les plugins installés
gst-inspect-1.0 | grep -i nvidia

# Vérifier nvarguscamerasrc
gst-inspect-1.0 nvarguscamerasrc

# Version de GStreamer
gst-launch-1.0 --version
```

## Tests de capture GStreamer

### Test simple (10 secondes)
```bash
gst-launch-1.0 nvarguscamerasrc num-buffers=300 sensor-id=0 ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=30/1' ! \
  fakesink
```

### Test avec affichage (nécessite écran)
```bash
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=30/1' ! \
  nvvidconv flip-method=0 ! 'video/x-raw, format=BGRx' ! \
  xvimagesink
```

### Test avec sauvegarde image
```bash
gst-launch-1.0 nvarguscamerasrc num-buffers=1 ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=30/1' ! \
  nvvidconv ! 'video/x-raw, format=BGRx' ! \
  videoconvert ! 'video/x-raw, format=BGR' ! \
  jpegenc ! filesink location=test_csi.jpg
```

### Test avec sauvegarde vidéo (10 secondes)
```bash
gst-launch-1.0 nvarguscamerasrc num-buffers=300 ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=30/1' ! \
  omxh264enc ! qtmux ! filesink location=test_csi.mp4
```

## Tests avec nvgstcapture (outil Jetson)

### Capture photo
```bash
nvgstcapture-1.0 --mode=1 --image-res=3
```

### Capture vidéo
```bash
nvgstcapture-1.0 --mode=2 --video-res=3
```

### Mode interactif
```bash
nvgstcapture-1.0
# Commandes dans l'interface:
# j : Capturer une photo
# 1 : Démarrer l'enregistrement vidéo
# 0 : Arrêter l'enregistrement
# q : Quitter
```

## Tests OpenCV

### Vérifier support GStreamer dans OpenCV
```bash
python3 -c "import cv2; print(cv2.getBuildInformation())" | grep -i gstreamer
```

### Test de capture avec OpenCV
```python
import cv2

gst = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=30/1 ! "
    "nvvidconv ! video/x-raw, format=BGRx ! "
    "videoconvert ! video/x-raw, format=BGR ! "
    "appsink"
)

cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
print(f"Caméra ouverte: {cap.isOpened()}")

if cap.isOpened():
    ret, frame = cap.read()
    print(f"Frame capturée: {ret}, Shape: {frame.shape if ret else 'N/A'}")
    cap.release()
```

## Paramètres avancés nvarguscamerasrc

### Exposition manuelle
```bash
gst-launch-1.0 nvarguscamerasrc sensor-id=0 \
  exposuretimerange="10000000 30000000" ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1' ! \
  fakesink
```

### Contrôle du gain
```bash
gst-launch-1.0 nvarguscamerasrc sensor-id=0 \
  gainrange="1 8" ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1' ! \
  fakesink
```

### Balance des blancs
```bash
# wbmode: 0=off, 1=auto, 2-9=divers presets
gst-launch-1.0 nvarguscamerasrc sensor-id=0 \
  wbmode=1 ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1' ! \
  fakesink
```

### Toutes les options
```bash
gst-launch-1.0 nvarguscamerasrc sensor-id=0 \
  sensor-mode=0 \
  exposuretimerange="10000000 30000000" \
  gainrange="1 8" \
  wbmode=1 \
  aeantibanding=1 \
  tnr-mode=1 \
  tnr-strength=0.5 \
  ee-mode=1 \
  ee-strength=0.5 ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1' ! \
  fakesink
```

## Performance et monitoring

### Surveiller l'utilisation GPU
```bash
# Installation de jetson-stats
sudo -H pip3 install jetson-stats

# Monitoring en temps réel
sudo jtop
```

### Activer le mode performance
```bash
# Mode performance maximum
sudo nvpmodel -m 0
sudo jetson_clocks

# Voir les modes disponibles
sudo nvpmodel -q

# Revenir au mode par défaut
sudo nvpmodel -m 1
```

### Vérifier la température
```bash
cat /sys/devices/virtual/thermal/thermal_zone*/temp
```

## Dépannage

### La caméra n'est pas détectée

1. Vérifier la connexion physique du câble CSI
2. Redémarrer la Jetson
```bash
sudo reboot
```

3. Vérifier les messages du kernel
```bash
dmesg | grep -i camera
dmesg | grep -i imx219
```

4. Recharger le driver
```bash
sudo modprobe -r imx219
sudo modprobe imx219
```

### Erreur "No cameras available"

```bash
# Vérifier les permissions
ls -la /dev/video*
sudo chmod 666 /dev/video*

# Ajouter l'utilisateur au groupe video
sudo usermod -aG video $USER
# Déconnexion/reconnexion nécessaire
```

### Pipeline GStreamer échoue

1. Tester chaque élément séparément
```bash
gst-inspect-1.0 nvarguscamerasrc
gst-inspect-1.0 nvvidconv
gst-inspect-1.0 videoconvert
```

2. Vérifier les capacités
```bash
gst-inspect-1.0 nvarguscamerasrc | grep -A 10 "Pad Templates"
```

3. Activer les logs debug
```bash
GST_DEBUG=3 gst-launch-1.0 nvarguscamerasrc ! fakesink
```

### OpenCV ne supporte pas GStreamer

Recompiler OpenCV avec GStreamer :
```bash
# Installer les dépendances
sudo apt-get install libgstreamer1.0-dev \
                     libgstreamer-plugins-base1.0-dev \
                     libgstreamer-plugins-good1.0-dev \
                     libgstreamer-plugins-bad1.0-dev

# Lors de la compilation OpenCV
cmake -D WITH_GSTREAMER=ON \
      -D WITH_CUDA=ON \
      -D CUDA_ARCH_BIN="5.3,6.2,7.2" \
      ...
```

## Tests de performance

### Mesurer le FPS réel
```bash
gst-launch-1.0 nvarguscamerasrc num-buffers=300 ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1' ! \
  fpsdisplaysink text-overlay=false video-sink=fakesink sync=false
```

### Benchmark différentes résolutions
```bash
# 1080p @ 30 FPS
time gst-launch-1.0 nvarguscamerasrc num-buffers=300 ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1' ! \
  fakesink

# 720p @ 60 FPS
time gst-launch-1.0 nvarguscamerasrc num-buffers=600 ! \
  'video/x-raw(memory:NVMM), width=1280, height=720, framerate=60/1' ! \
  fakesink
```

## Scripts utiles

### Capturer une photo test
```bash
#!/bin/bash
gst-launch-1.0 nvarguscamerasrc num-buffers=1 ! \
  'video/x-raw(memory:NVMM), width=3280, height=2464, framerate=21/1' ! \
  nvvidconv ! jpegenc quality=95 ! \
  filesink location="capture_$(date +%Y%m%d_%H%M%S).jpg"
```

### Enregistrer 10 secondes de vidéo
```bash
#!/bin/bash
gst-launch-1.0 nvarguscamerasrc num-buffers=300 ! \
  'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1' ! \
  omxh264enc bitrate=8000000 ! \
  'video/x-h264, stream-format=byte-stream' ! \
  h264parse ! qtmux ! \
  filesink location="video_$(date +%Y%m%d_%H%M%S).mp4"
```

## Ressources

- NVIDIA Jetson Camera: https://developer.nvidia.com/embedded/learn/tutorials/first-picture-csi-usb-camera
- GStreamer Jetson Wiki: https://developer.ridgerun.com/wiki/index.php?title=Jetson_Nano/Gstreamer
- nvarguscamerasrc doc: https://docs.nvidia.com/jetson/l4t-multimedia/group__libarguscapture.html
