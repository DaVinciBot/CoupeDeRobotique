#!/bin/bash
# Script de test rapide pour la version simplifiée

echo "🚀 Test de la version simplifiée Jetson ArUco Detector"
echo ""

# Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo "📝 Création du fichier .env depuis .env.example.new..."
    cp .env.example.new .env
    echo "✅ Fichier .env créé"
    echo ""
fi

# Afficher la configuration actuelle
echo "📋 Configuration actuelle:"
echo "   CALIBRATE_MODE=$(grep CALIBRATE_MODE .env | cut -d'=' -f2)"
echo "   DEBUG_MODE=$(grep DEBUG_MODE .env | cut -d'=' -f2)"
echo "   SHOW_ARENA=$(grep SHOW_ARENA .env | cut -d'=' -f2)"
echo "   SHOW_CAMERA_FEED=$(grep SHOW_CAMERA_FEED .env | cut -d'=' -f2)"
echo ""

# Proposer le choix
echo "Que voulez-vous faire ?"
echo "1) Calibration"
echo "2) Détection ArUco"
echo "3) Détection ArUco (mode DEBUG)"
echo ""
read -p "Votre choix (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🎯 Lancement de la CALIBRATION..."
        echo "   Suivez les instructions à l'écran"
        echo "   Appuyez sur 'c' pour capturer une image"
        echo "   Appuyez sur 'q' pour terminer"
        echo ""
        
        # Activer le mode calibration temporairement
        sed -i.bak 's/CALIBRATE_MODE=.*/CALIBRATE_MODE=True/' .env
        python main_simplified.py
        sed -i.bak 's/CALIBRATE_MODE=.*/CALIBRATE_MODE=False/' .env
        rm .env.bak
        
        echo ""
        echo "💡 N'oubliez pas de copier les résultats dans votre .env !"
        ;;
        
    2)
        echo ""
        echo "🎯 Lancement de la DÉTECTION..."
        echo "   Appuyez sur 'Q' ou 'ESC' pour quitter"
        echo ""
        
        python main_simplified.py
        ;;
        
    3)
        echo ""
        echo "🎯 Lancement de la DÉTECTION (mode DEBUG)..."
        echo "   Les statistiques seront affichées dans le terminal"
        echo "   Appuyez sur 'Q' ou 'ESC' pour quitter"
        echo ""
        
        # Activer le mode debug temporairement
        sed -i.bak 's/DEBUG_MODE=.*/DEBUG_MODE=True/' .env
        python main_simplified.py
        sed -i.bak 's/DEBUG_MODE=.*/DEBUG_MODE=False/' .env
        rm .env.bak
        ;;
        
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "✅ Terminé"
