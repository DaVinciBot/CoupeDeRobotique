#pragma once
#include <Arduino.h>

class Gs2Lidar {
public:
    Gs2Lidar(HardwareSerial& port,uint8_t rx,uint8_t tx,
             uint16_t obstacle_mm = 116,      // seuil obstacle
             uint16_t cliff_mm    = 130);     // seuil vide

    void   begin();
    void   task();

    bool   obstacleDetected() const;          // dist < obstacle_mm
    bool   cliffDetected()    const;          // dist > cliff_mm
    void   setCliffThreshold(uint16_t mm) { _cliffTh = mm; }

private:
    static constexpr uint16_t PACKET_SIZE = 322;
    static constexpr uint8_t  ENV_SIZE    = 2;
    static constexpr uint16_t POINT_COUNT = 160;
    static constexpr uint8_t  FRONT_START = 40;
    static constexpr uint8_t  FRONT_END   = 120;
    static constexpr uint8_t  FRONT_MIDDLE   = 80;

    void processPacket(const uint8_t* p);

    HardwareSerial& _serial;
    uint8_t  _rxPin, _txPin;
    uint16_t _obsTh, _cliffTh;
    uint8_t  _buf[PACKET_SIZE];
    uint16_t _idx = 0;
    bool     _obstacle = false;
    bool     _cliff    = false;
};