#include <crc.h>


byte CRC::digest(byte *data, byte size)
{
    // create a 8 bit CRC
    byte crc = 0;
    for (byte i = 0; i < size; i++)
        crc = this->table[crc ^ data[i]];
    return crc;
}