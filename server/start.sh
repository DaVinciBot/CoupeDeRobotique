clear
# Démarre en arrière plan chromium, en fullscreen et mute la sortie 
export DISPLAY=:0
chromium-browser --start-fullscreen --start-maximized file:///home/dvb/Desktop/CoupeDeRobotique/RC/WebUI/index.html &> /dev/null &
# Démarre le serveur websocket
cd /home/dvb/Desktop/CoupeDeRobotique/RC/API
source ./api/bin/activate
python ./api.py
