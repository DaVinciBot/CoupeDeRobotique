import serial.tools.list_ports


def get_all_serial_number():
    ports = serial.tools.list_ports.comports()
    print(f"Number of ports: {len(ports)}")
    for port in ports:
        print(f"Serial Number: {port.serial_number}")
