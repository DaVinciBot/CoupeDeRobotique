#import Libraries.Teensy_Com as teensy
from classes.tools import*
from classes.constants import SERVOS_PIN

# check that the dichotomic serach is working correctly
print(is_in_tab(SERVOS_PIN,8))
print(is_in_tab(SERVOS_PIN,-2))
print(is_in_tab(SERVOS_PIN,5))


