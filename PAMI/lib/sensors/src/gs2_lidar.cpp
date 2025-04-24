#include "gs2_lidar.hpp"

Gs2Lidar::Gs2Lidar(HardwareSerial& port,uint8_t rx,uint8_t tx,
                   uint16_t obstacle_mm,uint16_t cliff_mm)
: serial_(port), rxPin_(rx), txPin_(tx), obsTh_(obstacle_mm), cliffTh_(cliff_mm) {}

void Gs2Lidar::begin() {
    serial_.begin(921600, SERIAL_8N1, rxPin_, txPin_);
    delay(400);
    const uint8_t scanCmd[9] = {0xA5,0xA5,0xA5,0xA5,0x00,0x63,0x00,0x00,0x63};
    serial_.write(scanCmd, sizeof(scanCmd));
}

void Gs2Lidar::task() {
    while (serial_.available()) {
        buf_[idx_] = serial_.read();
        if (++idx_ == PACKET_SIZE) {
            processPacket(buf_);
            idx_ = 0;
        }
    }
}

bool Gs2Lidar::obstacleDetected() const { return obstacle_; }
bool Gs2Lidar::cliffDetected()    const { return cliff_;    }

void Gs2Lidar::processPacket(const uint8_t* p)
{
    obstacle_ = false;
    cliff_    = false;

    for (uint8_t i = FRONT_START; i <= FRONT_END; ++i) {
        uint16_t raw  = (static_cast<uint16_t>(p[ENV_SIZE + i*2 + 1]) << 8)
                      |  p[ENV_SIZE + i*2];
        uint16_t dist = raw & 0x01FF;                // 9 bits distance mm
                         

        if (!obstacle_ && dist < obsTh_){
          obstacle_ = true; // true si il y a un obstacle devant
        }
        if (i == FRONT_MIDDLE && !cliff_ && dist > cliffTh_){
          cliff_    = true; // true si il y a le vide
        }
        if (obstacle_ && cliff_) break;            
    }
}
