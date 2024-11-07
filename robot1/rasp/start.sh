# Open the (known) path to the script on robot1
cd /home/dvb/CoupeDeRobotique/robot1/rasp
# Source the venv
source venv/bin/activate

# Use the selected options
python main.py "$@"
