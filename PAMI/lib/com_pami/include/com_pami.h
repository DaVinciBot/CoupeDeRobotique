#ifndef COM_PAMI_H
#define COM_PAMI_H

#include <SX126x.h>
#include <crc.h>
#include <messages_pami.h>
#include <cstring>  // To use memcpy()

/**
 * @brief Structure holding the last sent/received message contents.
 *
 * Used to store a copy of the last message for possible retransmission or
 * inspection. The fixed-size buffer mirrors the maximum expected message size.
 */
struct last_message {
    byte size;      ///< Size of the message in bytes
    byte msg[256];  ///< Content of the message
};

/**
 * @brief Communication (LoRa) helper class.
 *
 * Encapsulates configuration and basic operations for the SX126x LoRa radio
 * used in this project. Responsibilities include radio initialization,
 * sending messages, printing text over the link, buffering incoming bytes,
 * and dispatching callbacks for received messages.
 *
 * @note This class holds an internal buffer and a pointer to a last_message
 * instance which are allocated when the object is constructed.
 */
class Com {
   public:
    /**
     * @brief Construct a new Com object
     *
     * Initializes internal members. Radio hardware must still be started by
     * calling begin().
     *
     */
    Com();

    /**
     * @brief Destroy the Com object
     *
     */
    ~Com();

    /**
     * @brief Initialize the LoRa radio with given control pins.
     *
     * @param nss Chip select pin for the SX126x
     * @param reset Reset pin for the SX126x
     * @param busy Busy pin for the SX126x
     * @return true on success
     * @return false on failure
     */
    bool begin(int8_t nss, int8_t reset, int8_t busy);

    /**
     * @brief Send a raw message over LoRa.
     *
     * @param msg Pointer to the byte buffer to send
     * @param size Number of bytes to send (must be <= 256)
     * @param is_nack If true, mark this message as a NACK (negative ack)
     */
    void send_msg(byte* msg, byte size, bool is_nack = false);

    /**
     * @brief Send a null-terminated text string over the radio.
     *
     * Convenience helper that wraps text into the radio message format.
     *
     * @param text C-string to send
     */
    void print(char* text);

    /**
     * @brief Install a callback table invoked on message reception.
     *
     * The supplied array should contain function pointers indexed by message
     * type (0..255). When a message is received, the appropriate callback is
     * called with the message buffer and its size.
     *
     * @param functions Array of 256 function pointers taking (byte* msg, byte
     * size)
     */
    void handle_callback(void (*functions[256])(byte* msg, byte size));

   private:
    /**
     * @brief Internal handler that processes radio events / incoming bytes.
     *
     * @return a status byte or the size of processed data depending on
     * internal conventions.
     */
    byte handle();

    /**
     * @brief Read bytes from the radio into the internal buffer and return
     * a pointer to that buffer.
     *
     * @return pointer to internal buffer containing the latest received data
     */
    byte* read_buffer();

    SX126x LoRa;  // Underlying radio object

    /* Radio configuration parameters */
    int sf = 7;               // LoRa spreading factor
    int bw = 125000;          // Bandwidth
    int cr = 5;               // Coding rate
    int preambleLength = 12;  // Preamble length
    bool crcType = true;      // CRC type

    int message_len = 256;                        // Maximum message length
    uint16_t syncWord = 0x3444;                   // Sync word
    uint8_t headerType = SX126X_HEADER_EXPLICIT;  // Header type

    byte* buffer = new byte[256];  // Internal buffer for storing received data
    int pointer = 0;               // Pointer to the buffer
    byte signature[4];  // Signature used to validate messages (default:
                        // END_BYTES_SIGNATURE) initialized in the constructor

    last_message* last_msg = new last_message();  // Pointer to the last sent
                                                  // message for retransmission
};

#endif
