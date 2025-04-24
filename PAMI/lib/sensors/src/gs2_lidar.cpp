
#include "gs2_lidar.hpp"

Gs2Lidar::Gs2Lidar(HardwareSerial& port,
                   uint8_t rx, uint8_t tx,
                   uint16_t seuil_mm)
: serial_(port), rxPin_(rx), txPin_(tx), seuil_(seuil_mm) {}

void Gs2Lidar::begin()
{
    serial_.begin(921600, SERIAL_8N1, rxPin_, txPin_);
    delay(400);
    const uint8_t scanCmd[9] = {0xA5,0xA5,0xA5,0xA5,0x00,0x63,0x00,0x00,0x63};
    serial_.write(scanCmd, sizeof(scanCmd));
}

void Gs2Lidar::task()
{
    while (serial_.available())
    {
        buf_[idx_++] = serial_.read();
        if (idx_ == PACKET_SIZE)
        {
            processPacket(buf_);
            idx_ = 0;
        }
    }
}

bool Gs2Lidar::obstacleDetected() const { return obstacle_; }

void Gs2Lidar::processPacket(const uint8_t* p)
{
    obstacle_ = false;
    for (uint16_t i = 0; i < POINT_COUNT; ++i)
    {
        uint16_t raw = (static_cast<uint16_t>(p[ENV_SIZE + i*2 + 1]) << 8)
                     |  p[ENV_SIZE + i*2];
        uint16_t dist = raw & 0x01FF;          // 9 bits = distance en mm
        if (dist > 0 && dist < seuil_)
        {
            obstacle_ = true;
            break;                             // inutile de poursuivre
        }
    }
}
