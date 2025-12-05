#!/usr/bin/env python3
"""Script de test pour déterminer le FPS maximum supporté par votre caméra.

Ce script teste différentes valeurs de FPS et vous indique laquelle fonctionne.
"""

import time

import cv2


def test_fps_setting(camera_id: int, target_fps: float, backends=None) -> bool:
    """Test si la caméra peut s'ouvrir avec un FPS donné.

    Args:
        camera_id: ID de la caméra
        target_fps: FPS à tester
        backends: Liste des backends OpenCV à essayer

    Returns:
        True si la caméra s'ouvre avec succès, False sinon
    """
    if backends is None:
        backends = [cv2.CAP_ANY]

    print(f"\n🧪 Test FPS={target_fps}...")

    for backend in backends:
        backend_name = {
            cv2.CAP_ANY: "CAP_ANY",
            cv2.CAP_V4L2: "CAP_V4L2",
            cv2.CAP_DSHOW: "CAP_DSHOW",
            cv2.CAP_MSMF: "CAP_MSMF",
        }.get(backend, f"Backend {backend}")

        cam = cv2.VideoCapture(camera_id, backend)

        if not cam.isOpened():
            cam.release()
            continue

        # Configurer le FPS
        cam.set(cv2.CAP_PROP_FPS, target_fps)
        time.sleep(0.2)  # Temps de stabilisation

        # Vérifier le FPS obtenu
        actual_fps = cam.get(cv2.CAP_PROP_FPS)

        # Essayer de lire quelques frames
        success_count = 0
        for _ in range(10):
            ret, _ = cam.read()
            if ret:
                success_count += 1
            time.sleep(0.01)

        cam.release()

        if success_count >= 5:  # Au moins 5 frames lues sur 10
            print(
                f"   ✅ {backend_name}: FPS demandé={target_fps}, obtenu={actual_fps:.1f}, frames lues={success_count}/10"
            )
            return True
        else:
            print(
                f"   ❌ {backend_name}: Échec (seulement {success_count}/10 frames lues)"
            )

    return False


def main():
    """Programme principal."""
    print("=" * 70)
    print("🎥 TEST DU FPS MAXIMUM DE VOTRE CAMÉRA")
    print("=" * 70)

    camera_id = 0

    # Backends à tester (adaptez selon votre OS)
    # Linux: CAP_V4L2
    # Windows: CAP_DSHOW, CAP_MSMF
    # macOS: CAP_ANY
    backends = [cv2.CAP_ANY]

    # Essayer d'ajouter les backends spécifiques
    for attr in ("CAP_V4L2", "CAP_DSHOW", "CAP_MSMF"):
        if hasattr(cv2, attr):
            backends.insert(0, getattr(cv2, attr))

    print(f"\n📹 Caméra ID: {camera_id}")
    print(f"🔧 Backends à tester: {len(backends)}")

    # Tester différentes valeurs de FPS
    fps_values = [30.0, 25.0, 20.0, 15.0, 10.0, 5.0]

    working_fps = []

    for fps in fps_values:
        if test_fps_setting(camera_id, fps, backends):
            working_fps.append(fps)

    print("\n" + "=" * 70)
    print("📊 RÉSULTATS")
    print("=" * 70)

    if working_fps:
        print(f"\n✅ FPS qui FONCTIONNENT: {working_fps}")
        print(f"\n💡 RECOMMANDATION:")
        print(f"   Dans votre fichier .env, utilisez:")
        print(f"   FPS={working_fps[0]}")
    else:
        print("\n❌ Aucun FPS n'a fonctionné !")
        print("   Essayez de laisser le FPS vide dans .env (utiliser le défaut)")
        print("   FPS=")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
