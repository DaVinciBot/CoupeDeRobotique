import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
print(ports.__len__())
for port in ports:
    print(f"Serial Number: {port.serial_number}")
