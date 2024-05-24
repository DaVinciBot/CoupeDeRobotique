import usb.core
import usb.util

def get_teensy_serial_number():
    # Find all USB devices
    devices = usb.core.find(find_all=True)
    
    for device in devices:
        # Check if the device is a Teensy by checking the idVendor and idProduct
        if device.idVendor == 0x16C0 and device.idProduct == 0x0483:
            # Read the serial number
            serial_number = usb.util.get_string(device, device.iSerialNumber)
            return serial_number

    return None

serial_number = get_teensy_serial_number()
if serial_number:
    print(f"Numéro de série de la Teensy: {serial_number}")
else:
    print("Aucune carte Teensy détectée")
