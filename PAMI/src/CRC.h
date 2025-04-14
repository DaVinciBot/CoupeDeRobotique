#ifndef CRC_H
#define CRC_H

#include <Arduino.h>

class CRC {
public:
    CRC(uint8_t polynomial = 0x07); // Default polynomial for CRC-8
    uint8_t digest(const uint8_t* data, size_t length);

private:
    uint8_t polynomial;
};

#endif // CRC_H
