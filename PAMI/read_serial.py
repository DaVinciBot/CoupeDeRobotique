#!/usr/bin/env python3
import serial
import time
import sys

PORT = "COM5"
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=2)
    print(f"[*] Connected to {PORT} at {BAUD} baud")
    print("[*] Waiting for data...")
    
    # Wait for initial boot messages
    time.sleep(3)
    
    # Read and print all available data
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            if data:
                print(data)
        else:
            time.sleep(0.1)
            
except KeyboardInterrupt:
    print("\n[*] Exiting...")
except Exception as e:
    print(f"[!] Error: {e}")
finally:
    if 'ser' in locals():
        ser.close()
