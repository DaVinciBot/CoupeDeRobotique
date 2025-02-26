try:
    from GPIO.gpio import PIN
except ImportError:
    pass
from GPIO.teensy_gpio_manager import TeensyGpioManager
