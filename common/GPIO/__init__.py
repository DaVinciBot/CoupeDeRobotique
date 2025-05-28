try:
    from GPIO.gpio import PIN
except ImportError:
    print("Failed to import GPIO module. Ensure the GPIO library is installed and accessible.")
    print("Falling back to dummy PIN class.")
    from GPIO.dummy_gpio import PIN
