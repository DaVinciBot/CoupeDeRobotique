#!/usr/bin/env python3
"""Script de test pour vérifier la compatibilité CSI IMX219."""

import sys

import cv2


def check_opencv_gstreamer():
    """Vérifie si OpenCV a été compilé avec le support GStreamer."""
    print("🔍 Vérification du support GStreamer dans OpenCV...")
    build_info = cv2.getBuildInformation()
    if "GStreamer" in build_info and "YES" in build_info.split("GStreamer")[1].split("\n")[0]:
        print("✅ OpenCV supporte GStreamer")
        return True
    else:
        print("❌ OpenCV ne supporte pas GStreamer")
        print("   Vous devez recompiler OpenCV avec -DWITH_GSTREAMER=ON")
        return False


def check_csi_device():
    """Vérifie si des périphériques vidéo sont disponibles."""
    print("\n🔍 Vérification des périphériques vidéo...")
    import os
    video_devices = [f"/dev/video{i}" for i in range(10) if os.path.exists(f"/dev/video{i}")]
    
    if video_devices:
        print(f"✅ Périphériques vidéo trouvés: {', '.join(video_devices)}")
        return True
    else:
        print("❌ Aucun périphérique vidéo trouvé")
        return False


def test_csi_camera(sensor_id=0, width=1920, height=1080, fps=30):
    """Teste l'ouverture et la capture avec une caméra CSI."""
    print(f"\n🎥 Test de la caméra CSI (sensor_id={sensor_id})...")
    
    gst_pipeline = (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        f"video/x-raw(memory:NVMM), width={width}, height={height}, "
        f"format=NV12, framerate={fps}/1 ! "
        f"nvvidconv flip-method=0 ! "
        f"video/x-raw, width={width}, height={height}, format=BGRx ! "
        f"videoconvert ! "
        f"video/x-raw, format=BGR ! "
        f"appsink"
    )
    
    print(f"   Pipeline: {gst_pipeline[:80]}...")
    
    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
    
    if not cap.isOpened():
        print("❌ Impossible d'ouvrir la caméra CSI")
        return False
    
    print("✅ Caméra CSI ouverte avec succès")
    
    # Essayer de lire quelques frames
    success_count = 0
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            success_count += 1
            if i == 0:
                print(f"✅ Frame capturée - Résolution: {frame.shape[1]}x{frame.shape[0]}")
    
    cap.release()
    
    if success_count >= 8:
        print(f"✅ Test réussi - {success_count}/10 frames capturées")
        return True
    else:
        print(f"⚠️  Problème de stabilité - seulement {success_count}/10 frames capturées")
        return False


def test_v4l2_camera(camera_id=0):
    """Teste l'ouverture avec V4L2 (caméra USB)."""
    print(f"\n🎥 Test de la caméra V4L2 (camera_id={camera_id})...")
    
    cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print("❌ Impossible d'ouvrir la caméra V4L2")
        return False
    
    print("✅ Caméra V4L2 ouverte avec succès")
    
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame capturée - Résolution: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
        return True
    else:
        print("❌ Impossible de capturer une frame")
        cap.release()
        return False


def main():
    """Fonction principale de test."""
    print("=" * 70)
    print("Test de compatibilité caméra CSI IMX219")
    print("=" * 70)
    
    # 1. Vérifier GStreamer
    has_gstreamer = check_opencv_gstreamer()
    
    # 2. Vérifier les périphériques
    has_devices = check_csi_device()
    
    # 3. Tester caméra CSI
    csi_works = False
    if has_gstreamer:
        csi_works = test_csi_camera()
        
        # Tester le second port CSI si le premier échoue
        if not csi_works:
            print("\n🔄 Tentative avec le port CSI 1...")
            csi_works = test_csi_camera(sensor_id=1)
    
    # 4. Tester caméra USB en fallback
    v4l2_works = test_v4l2_camera()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"Support GStreamer:     {'✅' if has_gstreamer else '❌'}")
    print(f"Périphériques vidéo:   {'✅' if has_devices else '❌'}")
    print(f"Caméra CSI:            {'✅' if csi_works else '❌'}")
    print(f"Caméra USB (V4L2):     {'✅' if v4l2_works else '❌'}")
    print("=" * 70)
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS")
    print("-" * 70)
    
    if csi_works:
        print("✅ Votre caméra CSI fonctionne parfaitement !")
        print("   Configurez votre .env avec :")
        print("   USE_CSI_CAMERA=True")
        print("   CAMERA_ID=0")
        print("   FPS=30")
    elif v4l2_works:
        print("⚠️  La caméra CSI ne fonctionne pas, mais la caméra USB est OK")
        print("   Configurez votre .env avec :")
        print("   USE_CSI_CAMERA=False")
        print("   CAMERA_ID=0")
        print("   FPS=15")
    else:
        print("❌ Aucune caméra détectée")
        print("   Vérifiez :")
        print("   - Connexion physique de la caméra")
        print("   - Installation de JetPack (pour CSI)")
        print("   - Permissions d'accès à /dev/video*")
        print("   - Redémarrez la Jetson")
    
    if not has_gstreamer and not csi_works:
        print("\n📦 Pour installer le support GStreamer :")
        print("   sudo apt-get install gstreamer1.0-tools \\")
        print("                        gstreamer1.0-plugins-good \\")
        print("                        gstreamer1.0-plugins-bad")
    
    print("-" * 70)
    
    return 0 if (csi_works or v4l2_works) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
