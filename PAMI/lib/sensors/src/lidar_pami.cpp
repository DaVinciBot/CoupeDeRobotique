#include "lidar_pami.h"

lidar_pami::lidar_pami(HardwareSerial &serialPort, int8_t rxPin, int8_t txPin, bool debug)
    : _serial(serialPort), _rxPin(rxPin), _txPin(txPin), _debug(debug) {}

void lidar_pami::begin(uint32_t baud)
{
    if (_debug && !Serial)
    { // Debug only: start USB‑Serial if present
        Serial.begin(115200);
        uint32_t t0 = millis(); // Wait max 2 s for host
        while (!Serial && (millis() - t0 < 2000))
        {
        }
    }

    _serial.begin(baud, SERIAL_8N1, _rxPin, _txPin);
    delay(100);
    sendScanCommand();

    if (_debug)
        Serial.println(F("lidar_pami: scan command sent"));
}

void lidar_pami::sendScanCommand()
{
    static const uint8_t cmd[9] = {
        0xA5, 0xA5, 0xA5, 0xA5,
        0x00, 0x63,
        0x00, 0x00,
        0x63};
    _serial.write(cmd, sizeof(cmd));
}

bool lidar_pami::readFrame()
{
    while (_serial.available() && _bufferIndex < PACKET_SIZE)
    {
        uint8_t b = _serial.read();

        if (_bufferIndex == 0 && b != FRAME_HEADER)
        {
            // skip until header byte found
            continue;
        }

        _buffer[_bufferIndex++] = b;
    }

    if (_bufferIndex == PACKET_SIZE)
    {
        _bufferIndex = 0; // ready for next packet after processing
        return true;
    }
    return false;
}

bool lidar_pami::obstacleAhead(uint16_t distanceMin)
{
    if (!readFrame())
        return false; // no complete frame yet

    float mean = 0.0f;
    uint16_t validCount = 0;

    for (uint16_t i = 0; i < POINT_COUNT; ++i)
    {
        uint16_t idx = HEADER_LEN + ENV_LEN + i * 2;
        uint16_t distance = ((uint16_t)_buffer[idx + 1] << 8) | _buffer[idx];
        distance &= 0x01FF; // keep 9 LSBs

        if (distance > 25 && distance < 300)
        {
            mean += distance;
            ++validCount;
        }
    }

    if (validCount == 0)
        return false; // no valid points
    mean /= validCount;
    Serial.print(F("Mean distance: "));
    Serial.println(mean);

    if (_debug)
    {
        Serial.print(F("Mean distance: "));
        Serial.println(mean);
    }

    return mean < distanceMin;
}
