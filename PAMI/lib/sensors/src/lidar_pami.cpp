#include "lidar_pami.h"

lidar_pami::lidar_pami(HardwareSerial& serialPort,
                       int8_t rxPin,
                       int8_t txPin,
                       bool debug)
    : _serial(serialPort), _rxPin(rxPin), _txPin(txPin), _debug(debug) {}

void lidar_pami::begin(uint32_t baud) {
    if (_debug && !Serial) {  // Debug only: start USB‑Serial if present
        Serial.begin(115200);
        uint32_t t0 = millis();  // Wait max 2 s for host
        while (!Serial && (millis() - t0 < 2000)) {
        }
    }

    _serial.begin(baud, SERIAL_8N1, _rxPin, _txPin);
    delay(100);
    sendScanCommand();

    Serial.println("lidar_pami: scan command sent");
}

void lidar_pami::sendScanCommand() {
    static const uint8_t cmd[9] = {0xA5, 0xA5, 0xA5, 0xA5, 0x00,
                                   0x63, 0x00, 0x00, 0x63};
    _serial.write(cmd, sizeof(cmd));
}

bool lidar_pami::readFrame() {
    while (_serial.available() && _bufferIndex < PACKET_SIZE) {
        uint8_t b = _serial.read();

        if (_bufferIndex == 0 && b != FRAME_HEADER) {
            continue;
        }

        _buffer[_bufferIndex++] = b;
    }

    if (_bufferIndex == PACKET_SIZE) {
        _bufferIndex = 0;  // ready for next packet after processing
        return true;
    }
    return false;
}

bool lidar_pami::obstacleAhead(uint16_t distanceMin) {
    float mean = 0.0f;
    uint16_t validCount = 0;

    for (uint16_t i = 0; i < POINT_COUNT; ++i) {
        uint16_t idx = HEADER_LEN + ENV_LEN + i * 2;
        uint16_t distance = ((uint16_t)_buffer[idx + 1] << 8) | _buffer[idx];
        distance &= 0x01FF;  // keep 9 LSBs

        if (distance > 25 && distance < 300) {
            mean += distance;
            ++validCount;
        }
    }

    if (validCount == 0)
        return false;  // no valid points
    mean /= validCount;

    Serial.printf("Mean distance: %f\n", mean);

    return mean < distanceMin;
}
bool lidar_pami::obstacleDirectlyAhead(uint16_t distanceMin) {
    // On initialise le minimum à une valeur très haute (plus grande que la portée max de 300)
    uint16_t minDistance = 1000; 
    bool validPointFound = false;
    
    // On regarde le CENTRE (Index ~70 à ~90 sur les 160 points)
    // Cela correspond au "nez" du robot
    int startIdx = (POINT_COUNT / 2) - 10; 
    int endIdx   = (POINT_COUNT / 2) + 10; 

    for (int i = 0; i <= 20; ++i) {
        
        uint16_t idx = HEADER_LEN + ENV_LEN + (i * 2);
        
        // Reconstruction de la valeur sur 16 bits
        uint16_t raw = _buffer[idx] | (_buffer[idx + 1] << 8);
        uint16_t distance = raw & 0x01FF; // Masque 9 bits
        
        // --- LOGIQUE DE FILTRAGE ---
        
        // On ignore :
        // 1. Les 0 (erreurs ou trop près)
        // 2. Les valeurs > 300 (l'infini pour le GS2)
        // 3. Les valeurs < 25 (zone aveugle du capteur)
        if (distance > 25 && distance < 300) {
            
            // C'EST ICI QUE TOUT CHANGE :
            // On cherche la distance la plus PETITE (l'objet le plus proche)
            if (distance < minDistance) {
                minDistance = distance;
            }
            validPointFound = true;
        }
    }
    for (int i = 140; i <= 159; ++i) {
        
        uint16_t idx = HEADER_LEN + ENV_LEN + (i * 2);
        
        // Reconstruction de la valeur sur 16 bits
        uint16_t raw = _buffer[idx] | (_buffer[idx + 1] << 8);
        uint16_t distance = raw & 0x01FF; // Masque 9 bits
        
        // --- LOGIQUE DE FILTRAGE ---
        
        // On ignore :
        // 1. Les 0 (erreurs ou trop près)
        // 2. Les valeurs > 300 (l'infini pour le GS2)
        // 3. Les valeurs < 25 (zone aveugle du capteur)
        if (distance > 25 && distance < 300) {
            
            // C'EST ICI QUE TOUT CHANGE :
            // On cherche la distance la plus PETITE (l'objet le plus proche)
            if (distance < minDistance) {
                minDistance = distance;
            }
            validPointFound = true;
        }
    }
    
    // Si le capteur n'a rien vu de valide dans cette zone (que du noir ou du vide total)
    if (!validPointFound) return false; 
    
    // Si l'objet le plus proche est inférieur au seuil -> OBSTACLE !
    return minDistance < distanceMin;
}

bool lidar_pami::isTiretteOn(uint16_t threshold) {
    float mean = 0.0f;
    for (uint16_t i = 0; i < POINT_COUNT; ++i) {
        uint16_t idx = HEADER_LEN + ENV_LEN + i * 2;
        uint16_t distance = ((uint16_t)_buffer[idx + 1] << 8) | _buffer[idx];
        distance &= 0x01FF;                     // keep 9 LSBs
        mean += distance > 300 ? 0 : distance;  // ignore points > 300mm
    }
    mean /= POINT_COUNT;

    //Serial.printf("Mean distance: %f\n", mean);

    return mean < threshold;
}

bool lidar_pami::isTiretteOn(uint16_t threshold) {
    float mean = 0.0f;
    for (uint16_t i = 0; i < POINT_COUNT; ++i) {
        uint16_t idx = HEADER_LEN + ENV_LEN + i * 2;
        uint16_t distance = ((uint16_t)_buffer[idx + 1] << 8) | _buffer[idx];
        distance &= 0x01FF;                     // keep 9 LSBs
        mean += distance > 300 ? 0 : distance;  // ignore points > 300mm
    }
    mean /= POINT_COUNT;

    Serial.printf("Mean distance: %f\n", mean);

    return mean < threshold;
}

void lidar_pami::update() {
    if (_serial.available()) {
        if (readFrame()) {
            if (_onReceiveCallback != nullptr) {
                _onReceiveCallback();
            }
        }
    }
}

void lidar_pami::onReceive(void (*callback)()) {
    _onReceiveCallback = callback;
    Serial.println("lidar_pami: onReceive callback set");
}
