import serial.tools.list_ports

def find_usb_devices():
    devices = serial.tools.list_ports.comports()
    usb_devices = []
    for device in devices:
        if "USB" in device.description:  # Filtrer les périphériques USB
            usb_devices.append(device.device)
    return usb_devices

def get_serial_number(port):
    try:
        with serial.Serial(port) as ser:
            ser.write(b's')  # Envoyer une commande pour demander le numéro de série
            serial_number = ser.readline().strip().decode()
            return serial_number
    except serial.SerialException as e:
        print("Erreur lors de la communication avec le périphérique:", str(e))
        return None

if __name__ == "__main__":
    usb_devices = find_usb_devices()
    if usb_devices:
        print("Numéro de série des périphériques USB:")
        for device in usb_devices:
            serial_number = get_serial_number(device)
            if serial_number:
                print("Port:", device)
                print("Numéro de série:", serial_number)
            else:
                print("Port:", device)
                print("Impossible de récupérer le numéro de série.")
            print()
    else:
        print("Aucun périphérique USB trouvé.")
