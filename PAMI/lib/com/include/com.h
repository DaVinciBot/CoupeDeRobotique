#include <SX126x.h>
#include <crc.h>
#include <messages.h>
#include <cstring> // To use memcpy()

struct last_message
{
    byte size;     ///< Size of the message in bytes
    byte msg[256]; ///< Content of the message
};

class Com
{
public:
    Com();
    ~Com();
    void begin(int8_t nss, int8_t reset, int8_t busy, int8_t irq = 0, int8_t txen = 0, int8_t rxen = 0);
    void send_msg(byte *msg, byte size, bool is_nack = false);
    void print(char *text);
    void handle_callback(void (*functions[256])(byte *msg, byte size));

private:
    byte handle();
    byte *read_buffer();

    SX126x LoRa;

    int sf = 7;              // LoRa spreading factor
    int bw = 125000;         // Bandwidth
    int cr = 5;              // Coding rate
    int preambleLength = 12; // Preamble length
    bool crcType = true;     // CRC type

    int message_len = 256;                       // Maximum message length
    uint16_t syncWord = 0x3444;                  // Sync word
    uint8_t headerType = SX126X_HEADER_EXPLICIT; // Header type

    byte *buffer = new byte[256]; ///< Internal buffer for storing received data
    int pointer = 0;              // Pointer to the buffer
    byte signature[4];            ///< Signature used to validate messages (default: END_BYTES_SIGNATURE) initialized in the constructor

    last_message *last_msg = new last_message(); ///< Pointer to the last sent message for retransmission
};