#ifndef lidar_scanner_h
#define lidar_scanner_h

#include <Arduino.h>

class lidar_pami
{
public:
    static constexpr uint32_t DEFAULT_BAUD = 921600;

    /**
     * @param serialPort  Reference to the UART used by the LIDAR (default Serial1)
     * @param rxPin       UART RX pin (default 44)
     * @param txPin       UART TX pin (default 43)
     * @param debug       If true, prints debug messages on Serial
     */
    lidar_pami(HardwareSerial &serialPort,
               int8_t rxPin = -1,
               int8_t txPin = -1,
               bool debug = false);

    void begin(uint32_t baud = DEFAULT_BAUD);

    bool obstacleAhead(uint16_t distanceMin = 100);
    bool isTiretteOn(uint16_t threshold = 5);
    void loop();
    void onReceive(void (*callback)());

private:
    static const uint16_t PACKET_SIZE = 331;
    static const uint8_t FRAME_HEADER = 0xA5;
    static const uint8_t HEADER_LEN = 8;
    static const uint8_t ENV_LEN = 2;
    static const uint16_t POINT_COUNT = 160;

    HardwareSerial &_serial;
    int8_t _rxPin;
    int8_t _txPin;
    bool _debug;

    uint8_t _buffer[PACKET_SIZE];
    uint16_t _bufferIndex = 0;

    void (*_onReceiveCallback)() = nullptr;

    bool readFrame();
    void sendScanCommand();
};

#endif // LIDAR_SCANNER_H
