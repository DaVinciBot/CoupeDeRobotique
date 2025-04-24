#pragma once
#include <Arduino.h>

/*  Classe minimaliste pour YDLIDAR GS2 ------------------------------------ */
/*  – begin()  : initialise le port série et démarre le scan                */
/*  – task()   : à appeler à chaque loop ; lit le flux et met à jour l’état */
/*  – obstacleDetected() : true ↔ au moins un point < seuil_mm              */
class Gs2Lidar {
public:
    Gs2Lidar(HardwareSerial& port,
             uint8_t rxPin, uint8_t txPin,
             uint16_t seuil_mm = 100 /* mm */);

    void   begin();
    void   task();                       // à appeler très souvent
    bool   obstacleDetected() const;     // true si dist < seuil_mm

private:
    static constexpr uint16_t PACKET_SIZE  = 322;
    static constexpr uint8_t  ENV_SIZE     = 2;
    static constexpr uint16_t POINT_COUNT  = 160;

    void   processPacket(const uint8_t* p);

    HardwareSerial& serial_;
    uint8_t  rxPin_, txPin_;
    uint16_t seuil_;
    uint8_t  buf_[PACKET_SIZE];
    uint16_t idx_  = 0;
    bool     obstacle_ = false;
};
