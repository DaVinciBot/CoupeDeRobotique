#include <com_pami.h>

Com::Com() {
    // Initialize the buffer
    for (uint16_t k = 0; k < 256; k++)
        this->buffer[k] = 0;
}

Com::~Com() {
    if (loraSerial) {
        loraSerial->end();
    }
}

bool Com::begin(int8_t rx_pin, int8_t tx_pin, uint32_t baud) {
    Serial.println("Initializing DX-LR01 LoRa module via UART");
    
    // Use Serial2 for communication with DX-LR01
    loraSerial = &Serial2;
    
    // Initialize UART with specified pins and baudrate
    loraSerial->begin(baud, SERIAL_8N1, rx_pin, tx_pin);
    
    if (!loraSerial) {
        Serial.println("[ERROR] Failed to initialize Serial2 for DX-LR01");
        return false;
    }
    
    delay(100);  // Wait for module to be ready
    
    Serial.println("DX-LR01 initialized at " + String(baud) + " baud");
    Serial.println("RX pin: " + String(rx_pin) + ", TX pin: " + String(tx_pin));
    
    initialized = true;
    return true;
}

void Com::send_msg(byte* msg, byte size, bool is_nack) {
    if (!initialized || !loraSerial) {
        Serial.println("[ERROR] LoRa not initialized");
        return;
    }
    
    // Send directly via UART to DX-LR01
    loraSerial->write(msg, size);
    loraSerial->flush();
    
    Serial.print("LoRa TX: ");
    for (int i = 0; i < size; i++) {
        Serial.print(String(msg[i], HEX) + " ");
    }
    Serial.println();
}

void Com::print(char* text) {
    if (!initialized || !loraSerial) {
        Serial.println("[ERROR] LoRa not initialized");
        return;
    }
    
    // Send text directly via UART
    loraSerial->print(text);
    loraSerial->flush();
    
    Serial.println("LoRa TX: " + String(text));
}

void Com::handle_callback(void (*functions[256])(byte* msg, byte size)) {
    // Store callback functions
    for (int i = 0; i < 256; i++) {
        callbacks[i] = functions[i];
    }
}

int Com::update() {
    if (!initialized || !loraSerial) {
        return 0;
    }
    
    int bytes_read = 0;
    
    // Read available data from UART
    while (loraSerial->available() && buffer_index < 256) {
        buffer[buffer_index++] = loraSerial->read();
        bytes_read++;
    }
    
    // If we have received data and a reasonable timeout has passed, process it
    if (buffer_index > 0) {
        delay(50);  // Small delay to allow more data to arrive
        
        // Check for more data after delay
        while (loraSerial->available() && buffer_index < 256) {
            buffer[buffer_index++] = loraSerial->read();
            bytes_read++;
        }
        
        // If no more data arrives, consider the message complete
        if (!loraSerial->available() && buffer_index > 0) {
            // Store the last received message
            last_received_size = buffer_index;
            memcpy(last_received, buffer, buffer_index);
            
            // Call callback if it exists for this message type
            byte msg_type = buffer[0];
            if (callbacks[msg_type] != nullptr) {
                callbacks[msg_type](buffer, buffer_index);
            }
            
            // Display received data in multiple formats
            Serial.println("\n[LoRa RX] Message received! Size: " + String(buffer_index) + " bytes");
            
            // Display as HEX
            Serial.print("[LoRa RX HEX] ");
            for (int i = 0; i < buffer_index; i++) {
                Serial.print(String(buffer[i], HEX) + " ");
            }
            Serial.println();
            
            // Display as ASCII (if printable)
            Serial.print("[LoRa RX ASCII] ");
            for (int i = 0; i < buffer_index; i++) {
                if (buffer[i] >= 32 && buffer[i] <= 126) {
                    Serial.print((char)buffer[i]);
                } else {
                    Serial.print("[" + String(buffer[i]) + "]");
                }
            }
            Serial.println("\n");
            
            // Reset buffer
            buffer_index = 0;
            for (int i = 0; i < 256; i++) {
                buffer[i] = 0;
            }
        }
    }
    
    return bytes_read;
}

byte* Com::getLastMessage(int* out_size) {
    if (out_size != nullptr) {
        *out_size = last_received_size;
    }
    return last_received;
}
