#include "lidar.h"

Gs2Lidar::Gs2Lidar(HardwareSerial& port,uint8_t rx,uint8_t tx,
                   uint16_t obstacle_mm,uint16_t cliff_mm)
: _serial(port), _rxPin(rx), _txPin(tx), _obsTh(obstacle_mm), _cliffTh(cliff_mm) {}

void Gs2Lidar::begin() {
    _serial.begin(921600, SERIAL_8N1, _rxPin, _txPin);
    delay(400);
    const uint8_t scanCmd[9] = {0xA5,0xA5,0xA5,0xA5,0x00,0x63,0x00,0x00,0x63};
    _serial.write(scanCmd, sizeof(scanCmd));
}

void Gs2Lidar::task() {
    while (_serial.available()) {
        _buf[_idx] = _serial.read();
        if (++_idx == PACKET_SIZE) {
            processPacket(_buf);
            _idx = 0;
        }
    }
}

bool Gs2Lidar::obstacleDetected() const { return _obstacle; }
bool Gs2Lidar::cliffDetected()    const { return _cliff;    }

void Gs2Lidar::processPacket(const uint8_t* p)
{
    _obstacle = false;
    _cliff    = false;

    for (uint8_t i = FRONT_START; i <= FRONT_END; ++i) {
        uint16_t raw  = (static_cast<uint16_t>(p[ENV_SIZE + i*2 + 1]) << 8)
                      |  p[ENV_SIZE + i*2];
        uint16_t dist = raw & 0x01FF;                // 9 bits distance mm
                         

        if (!_obstacle && dist < _obsTh){
          _obstacle = true; // true si il y a un obstacle devant
        }
        if (i == FRONT_MIDDLE && !_cliff && dist > _cliffTh){
          _cliff    = true; // true si il y a le vide
        }
        if (_obstacle && _cliff) break;            
    }
}