# 🚀 Guide de migration vers la version simplifiée

## 📋 Vue d'ensemble

Cette migration simplifie drastiquement le code tout en conservant toutes les fonctionnalités.

**Temps estimé** : 5-10 minutes  
**Risque** : Faible (backup automatique)  
**Avantages** : Code -37% plus court, -54% de configuration

---

## ✅ Pré-requis

- [ ] Jetson Nano avec caméra CSI IMX219
- [ ] Python 3.8+
- [ ] OpenCV avec support GStreamer
- [ ] Accès au dossier `/Users/clement/Documents/CoupeDeRobotique/jetson`

---

## 📦 Étape 1 : Backup (IMPORTANT !)

```bash
cd /Users/clement/Documents/CoupeDeRobotique/jetson
cp -r . ../jetson_backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Backup créé"
```

---

## 🧪 Étape 2 : Test de la nouvelle version

### 2.1 Créer la configuration
```bash
cp .env.example.new .env
```

### 2.2 Éditer `.env` si nécessaire
```bash
nano .env
```

Vérifier/modifier :
- `CAMERA_ID` (0 ou 1)
- `CAMERA_MATRIX` et `DIST_COEFFS` (si déjà calibré)
- `CHESSBOARD_COLS` et `CHESSBOARD_ROWS` (pour calibration)

### 2.3 Test de calibration
```bash
# Dans .env, mettre CALIBRATE_MODE=True
python main_simplified.py
```

Résultat attendu :
- ✅ Caméra s'ouvre en 1080p@15fps
- ✅ Détection d'échiquier fonctionne
- ✅ Capture d'images avec 'c'
- ✅ Sortie des matrices de calibration

### 2.4 Test de détection
```bash
# Dans .env, mettre CALIBRATE_MODE=False
python main_simplified.py
```

Résultat attendu :
- ✅ Détection ArUco fonctionne
- ✅ Affichage arena fonctionne
- ✅ Retour vidéo annoté
- ✅ FPS stable ~15fps

Si tout fonctionne → **Continuer à l'étape 3**  
Si problème → **Restaurer le backup** et signaler l'erreur

---

## 🔄 Étape 3 : Remplacement des fichiers

### 3.1 Remplacer main.py
```bash
mv main.py main_old.py
mv main_simplified.py main.py
```

### 3.2 Remplacer .env.example
```bash
mv .env.example .env.example.old
mv .env.example.new .env.example
```

### 3.3 Mettre à jour __init__.py
```bash
cat > src/camera/__init__.py << 'EOF'
"""Camera module for CSI camera on Jetson Nano."""

from .csi_camera import CSICamera

__all__ = ['CSICamera']
EOF
```

### 3.4 Archiver les anciens fichiers
```bash
mkdir -p src/camera/old
mv src/camera/camera.py src/camera/old/
mv src/camera/threaded_camera.py src/camera/old/
```

---

## ✨ Étape 4 : Test final

### 4.1 Vérifier les imports
```bash
python -c "from src.camera import CSICamera; print('✅ Import OK')"
```

### 4.2 Lancer la détection
```bash
python main.py
```

### 4.3 Vérifier les fonctionnalités
- [ ] Caméra démarre correctement
- [ ] Détection ArUco fonctionne
- [ ] Arena s'affiche
- [ ] FPS stable
- [ ] Peut quitter avec 'Q'

---

## 📊 Étape 5 : Vérification de la migration

### Checklist complète

#### Fichiers créés
- [ ] `src/camera/csi_camera.py` existe
- [ ] `main.py` est la version simplifiée
- [ ] `.env.example` est la version simplifiée
- [ ] `README_SIMPLIFIED.md` existe
- [ ] `ANALYSE_SIMPLIFICATION.md` existe

#### Fichiers archivés
- [ ] `main_old.py` existe
- [ ] `.env.example.old` existe
- [ ] `src/camera/old/camera.py` existe
- [ ] `src/camera/old/threaded_camera.py` existe

#### Fonctionnalités
- [ ] Calibration fonctionne
- [ ] Détection ArUco fonctionne
- [ ] Arena fonctionne
- [ ] Retour vidéo fonctionne
- [ ] Mode DEBUG fonctionne

---

## 🐛 Dépannage

### Problème : "ModuleNotFoundError: No module named 'src.camera.csi_camera'"

**Solution** :
```bash
# Vérifier que le fichier existe
ls -la src/camera/csi_camera.py

# Vérifier __init__.py
cat src/camera/__init__.py
```

---

### Problème : "RuntimeError: Échec ouverture caméra CSI"

**Causes possibles** :
1. Caméra pas connectée correctement
2. Pipeline GStreamer non disponible

**Solution** :
```bash
# Tester le pipeline manuellement
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=15/1' ! nvvidconv ! 'video/x-raw, format=BGRx' ! videoconvert ! 'video/x-raw, format=BGR' ! filesink location=/tmp/test.raw

# Si ça marche, le problème est ailleurs
# Si ça ne marche pas, vérifier :
dmesg | grep imx219
ls /dev/video*
```

---

### Problème : "Les marqueurs ne sont pas détectés"

**Vérifications** :
1. Calibration faite ? (`CAMERA_MATRIX` dans `.env`)
2. Au moins 3 marqueurs de référence visibles ? (IDs 20, 21, 22, 23)
3. Éclairage suffisant ?
4. Marqueurs bien imprimés et plats ?

---

### Problème : "L'arena ne s'affiche pas"

**Vérifications** :
```bash
# Vérifier dans .env
grep SHOW_ARENA .env  # Doit être True

# Vérifier matplotlib
python -c "import matplotlib; print('✅ OK')"

# Essayer en mode DEBUG
# Dans .env : DEBUG_MODE=True
python main.py
```

---

## 🔙 Rollback (en cas de problème)

### Restaurer l'ancienne version
```bash
# Revenir au backup
cd /Users/clement/Documents/CoupeDeRobotique
rm -rf jetson
cp -r jetson_backup_* jetson
cd jetson

# Ou restaurer fichier par fichier
mv main_old.py main.py
mv .env.example.old .env.example
mv src/camera/old/camera.py src/camera/
mv src/camera/old/threaded_camera.py src/camera/

# Restaurer __init__.py original
cat > src/camera/__init__.py << 'EOF'
"""Camera module for video capture and calibration."""

from .camera import Camera
from .threaded_camera import ThreadedCamera

__all__ = ['Camera', 'ThreadedCamera']
EOF
```

---

## 📈 Après la migration

### Nouvelles commandes

#### Lancement rapide
```bash
# Calibration
./run_simplified.sh  # Choisir option 1

# Détection
./run_simplified.sh  # Choisir option 2

# Détection avec debug
./run_simplified.sh  # Choisir option 3
```

#### Configuration simplifiée
```bash
# Éditer la config (11 paramètres au lieu de 24)
nano .env

# Paramètres essentiels seulement :
# - CALIBRATE_MODE (True/False)
# - DEBUG_MODE (True/False)
# - SHOW_ARENA (True/False)
# - SHOW_CAMERA_FEED (True/False)
# - CAMERA_ID (0 ou 1)
# + paramètres de calibration
```

---

## 📚 Documentation

Après la migration, consultez :

1. **`README_SIMPLIFIED.md`** : Vue d'ensemble de la version simplifiée
2. **`ANALYSE_SIMPLIFICATION.md`** : Détails techniques de la simplification
3. **`.env.example`** : Configuration commentée

---

## ✅ Validation finale

Une fois la migration terminée :

```bash
# Vérifier la structure
tree -L 2 src/

# Devrait afficher :
# src/
# ├── camera/
# │   ├── __init__.py
# │   ├── csi_camera.py
# │   └── old/
# ├── detector/
# │   ├── __init__.py
# │   └── detector.py
# └── utils/
#     ├── __init__.py
#     └── timing.py

# Compter les lignes de code
wc -l main.py src/camera/csi_camera.py
# Devrait être ~618 lignes total

# Compter les paramètres .env
grep -c "^[A-Z]" .env.example
# Devrait être 11

echo "✅ Migration réussie !"
```

---

## 🎉 Félicitations !

Vous avez simplifié le code de **37%** tout en gardant **100%** des fonctionnalités !

**Prochaines étapes** :
- [ ] Tester en conditions réelles
- [ ] Signaler les bugs éventuels
- [ ] Documenter vos cas d'usage spécifiques
- [ ] Contribuer des améliorations

---

## 📞 Support

En cas de problème :
1. Vérifier la section **Dépannage** ci-dessus
2. Consulter `ANALYSE_SIMPLIFICATION.md` pour comprendre les changements
3. Restaurer le backup si nécessaire
4. Signaler l'erreur avec les logs complets

---

**Date de migration** : _______________  
**Version** : Simplified v1.0  
**Status** : ⬜ En cours | ⬜ Réussie | ⬜ Rollback
