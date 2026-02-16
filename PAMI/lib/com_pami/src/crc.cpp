#include <crc.h>

/**
 * @brief Computes an 8-bit CRC checksum for the given data.
 *
 * This function calculates the CRC using a lookup table (precomputed for
 * efficiency). The CRC is updated iteratively for each byte in the data array.
 *
 * @param data Pointer to the array of data to compute the CRC for.
 * @param size The size of the data array (number of bytes).
 * @return The computed 8-bit CRC checksum.
 */
byte CRC::digest(byte* data, byte size) {
    // Initialize the CRC value to 0
    byte crc = 0;

    // Process each byte in the input data
    for (byte i = 0; i < size; i++) {
        // Update the CRC using the lookup table
        crc = this->table[crc ^ data[i]];
    }

    // Return the final CRC value
    return crc;
}
