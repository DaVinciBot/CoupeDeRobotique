#!/bin/bash
# Script rapide pour tester et diagnostiquer la caméra CSI IMX219
# Usage: ./quick_test_csi.sh

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  Test rapide caméra CSI IMX219 sur Jetson"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 1. Vérifier les périphériques vidéo
echo "📹 Périphériques vidéo disponibles:"
ls -la /dev/video* 2>/dev/null || echo "   ❌ Aucun périphérique vidéo trouvé"
echo ""

# 2. Vérifier GStreamer
echo "🔧 Vérification GStreamer..."
if gst-inspect-1.0 nvarguscamerasrc > /dev/null 2>&1; then
    echo "   ✅ nvarguscamerasrc disponible"
else
    echo "   ❌ nvarguscamerasrc non disponible (JetPack non installé?)"
fi
echo ""

# 3. Test rapide de capture (5 secondes)
echo "🎥 Test de capture CSI (5 secondes)..."
echo "   Appuyez sur Ctrl+C pour arrêter avant la fin"
echo ""

gst-launch-1.0 nvarguscamerasrc num-buffers=150 ! \
    'video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=30/1' ! \
    nvvidconv ! 'video/x-raw, format=BGRx' ! \
    videoconvert ! 'video/x-raw, format=BGR' ! \
    fakesink 2>&1 | grep -E "(Setting|ERROR|WARNING)" || true

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Test terminé"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "💡 Pour un test plus complet, lancez:"
echo "   python3 test_csi_camera.py"
echo ""
