"""Script de diagnostic pour identifier les problèmes de caméra."""

import cv2
import time
import sys

def test_camera_settings(camera_id=0):
    """Teste différentes configurations de caméra."""
    print(f"\n🔍 Diagnostic de la caméra ID={camera_id}\n")
    print("=" * 60)
    
    # Test 1: Backend par défaut
    print("\n📹 Test 1: Backend par défaut (CAP_ANY)")
    cam = cv2.VideoCapture(camera_id)
    
    if not cam.isOpened():
        print("❌ Impossible d'ouvrir la caméra")
        return
    
    # Informations de base
    width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cam.get(cv2.CAP_PROP_FPS)
    backend = cam.getBackendName() if hasattr(cam, 'getBackendName') else "unknown"
    fourcc = int(cam.get(cv2.CAP_PROP_FOURCC))
    
    print(f"   Backend: {backend}")
    print(f"   Résolution: {width}x{height}")
    print(f"   FPS configuré: {fps}")
    print(f"   FourCC: {fourcc}")
    
    # Test de vitesse de lecture réelle
    print("\n⏱️  Test de vitesse de lecture (5 secondes)...")
    frame_count = 0
    start_time = time.time()
    test_duration = 5.0
    
    while time.time() - start_time < test_duration:
        ret, frame = cam.read()
        if ret:
            frame_count += 1
        else:
            print("   ⚠️  Erreur de lecture de frame")
            break
    
    elapsed = time.time() - start_time
    actual_fps = frame_count / elapsed
    
    print(f"   Frames lues: {frame_count}")
    print(f"   Temps écoulé: {elapsed:.2f}s")
    print(f"   FPS réel: {actual_fps:.2f}")
    
    if actual_fps < 10:
        print("   ❌ FPS très bas ! Problème détecté")
    elif actual_fps < 20:
        print("   ⚠️  FPS bas")
    else:
        print("   ✅ FPS correct")
    
    cam.release()
    
    # Test 2: Avec résolution réduite
    print("\n📹 Test 2: Résolution réduite (640x480)")
    cam = cv2.VideoCapture(camera_id)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    actual_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"   Résolution obtenue: {actual_width}x{actual_height}")
    
    frame_count = 0
    start_time = time.time()
    
    while time.time() - start_time < 3.0:
        ret, frame = cam.read()
        if ret:
            frame_count += 1
    
    elapsed = time.time() - start_time
    actual_fps = frame_count / elapsed
    print(f"   FPS réel: {actual_fps:.2f}")
    
    if actual_fps > 20:
        print("   ✅ Meilleur avec résolution réduite!")
    
    cam.release()
    
    # Test 3: Essayer de forcer FPS
    print("\n📹 Test 3: Forcer FPS à 30")
    cam = cv2.VideoCapture(camera_id)
    cam.set(cv2.CAP_PROP_FPS, 30)
    
    configured_fps = cam.get(cv2.CAP_PROP_FPS)
    print(f"   FPS après set: {configured_fps}")
    
    frame_count = 0
    start_time = time.time()
    
    while time.time() - start_time < 3.0:
        ret, frame = cam.read()
        if ret:
            frame_count += 1
    
    elapsed = time.time() - start_time
    actual_fps = frame_count / elapsed
    print(f"   FPS réel: {actual_fps:.2f}")
    
    cam.release()
    
    # Test 4: Différents backends (Linux/Jetson)
    if sys.platform.startswith('linux'):
        print("\n📹 Test 4: Backend V4L2 (Linux)")
        cam = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
        
        if cam.isOpened():
            cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            cam.set(cv2.CAP_PROP_FPS, 30)
            
            frame_count = 0
            start_time = time.time()
            
            while time.time() - start_time < 3.0:
                ret, frame = cam.read()
                if ret:
                    frame_count += 1
            
            elapsed = time.time() - start_time
            actual_fps = frame_count / elapsed
            print(f"   FPS réel avec V4L2: {actual_fps:.2f}")
            
            if actual_fps > 20:
                print("   ✅ V4L2 fonctionne mieux!")
        else:
            print("   ❌ V4L2 non disponible")
        
        cam.release()
    
    # Recommandations
    print("\n" + "=" * 60)
    print("\n💡 Recommandations:")
    print()
    
    if actual_fps < 10:
        print("❌ PROBLÈME MAJEUR détecté:")
        print("   1. Vérifiez les pilotes de caméra (v4l2-ctl --list-devices)")
        print("   2. Essayez: sudo modprobe bcm2835-v4l2")
        print("   3. Vérifiez les permissions: sudo usermod -a -G video $USER")
        print("   4. Redémarrez après changements")
        print()
        print("   Pour Jetson, installez:")
        print("   sudo apt-get install v4l-utils")
        print("   v4l2-ctl --list-formats-ext")
    elif actual_fps < 15:
        print("⚠️  FPS sous-optimal:")
        print("   1. Réduire résolution dans .env:")
        print("      CAMERA_WIDTH=640")
        print("      CAMERA_HEIGHT=480")
        print("   2. Essayer backend V4L2")
        print("   3. Désactiver SHOW_ARENA=False")
    else:
        print("✅ Caméra fonctionne correctement!")
        print("   Si FPS traitement > FPS caméra, c'est normal avec threading")


if __name__ == "__main__":
    import sys
    camera_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    test_camera_settings(camera_id)
