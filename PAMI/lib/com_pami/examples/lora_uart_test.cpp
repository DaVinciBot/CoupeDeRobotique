/**
 * @brief Example: DX-LR01 LoRa Module UART Test
 * 
 * Simple test to verify communication with DX-LR01 module via UART.
 * 
 * Wiring (as specified):
 * - DX-LR01 VCC -> ESP32 3.3V
 * - DX-LR01 GND -> ESP32 GND
 * - DX-LR01 TXD -> ESP32 GPIO 16 (RX2)
 * - DX-LR01 RXD -> ESP32 GPIO 17 (TX2)
 * - DX-LR01 M0 -> GND (normal mode)
 * - DX-LR01 M1 -> GND (normal mode)
 * - DX-LR01 AUX -> Not connected (optional)
 * 
 * To use this, uncomment and call from main.cpp setup() and loop()
 */

#include <Arduino.h>
#include "com_pami.h"

// Global LoRa object
Com* lora = nullptr;

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("\n\n=== DX-LR01 LoRa UART Test ===\n");
    
    // Create and initialize LoRa module
    lora = new Com();
    
    // Initialize with config values: UART RX=16, TX=17, baud=9600
    if (lora->begin(16, 17, 9600)) {
        Serial.println("[OK] DX-LR01 initialized successfully");
    } else {
        Serial.println("[ERROR] Failed to initialize DX-LR01");
    }
    
    // Small delay before first transmission
    delay(500);
}

void loop() {
    // Test 1: Send text message every 5 seconds
    static unsigned long lastSend = 0;
    if (millis() - lastSend > 5000) {
        Serial.println("\n--- Sending test message ---");
        lora->print("Hello LoRa!");
        lastSend = millis();
    }
    
    // Test 2: Receive and process incoming data
    lora->update();
    
    delay(10);
}

/**
 * @brief Alternative test: Send binary messages
 * 
 * Uncomment to test binary message transmission
 */
/*
void loop_binary_test() {
    static unsigned long lastSend = 0;
    
    if (millis() - lastSend > 3000) {
        // Create a simple 4-byte message
        byte msg[4] = {0x01, 0x02, 0x03, 0x04};
        
        Serial.print("Sending binary: ");
        for (int i = 0; i < 4; i++) {
            Serial.print(String(msg[i], HEX) + " ");
        }
        Serial.println();
        
        lora->send_msg(msg, 4);
        lastSend = millis();
    }
    
    // Receive mode
    lora->update();
    
    delay(10);
}
*/

/**
 * @brief Continuous receive mode test
 * 
 * Uncomment to enable continuous listening for incoming messages
 */
/*
void loop_receive_only() {
    // Just listen and process incoming data
    lora->update();
    
    delay(100);
}
*/
