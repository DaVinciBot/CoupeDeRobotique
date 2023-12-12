from rasp.classes.tools import get_current_date
from rasp.classes.lidar import Lidar
from rasp.classes.pinInteract import PIN
from rasp.classes.arena import RectangleArena
from rasp.classes.point import point
import rasp.Libraries.Teensy_Com as teensy
import math

# Get arena
arena : RectangleArena = RectangleArena()

# Get Rolling_basis
rolling_basis = teensy.Rolling_basis()

rolling_basis.Go_To(x=1,y=1)