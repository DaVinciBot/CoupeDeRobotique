#ifndef COM_PAMI_H
#define COM_PAMI_H

#include <Arduino.h>
#include <HardwareSerial.h>
#include <cstring>

/**
 * @brief Communication (LoRa) helper class for DX-LR01 module.
 *
 * Encapsulates UART-based communication with the DX-LR01 LoRa module.
 * The module communicates via Serial2 (GPIO16 RX, GPIO17 TX at 9600 baud).
 *
 * Responsibilities include:
 * - UART initialization
 * - Sending messages over LoRa via UART
 * - Receiving and buffering incoming LoRa data
 * - Dispatching callbacks for received messages
 */
class Com {
   public:
    /**
     * @brief Construct a new Com object
     *
     * Initializes internal members.
     */
    Com();

    /**
     * @brief Destroy the Com object
     */
    ~Com();

    /**
     * @brief Initialize the DX-LR01 LoRa module via UART.
     *
     * Sets up Serial2 with the configure pins and baudrate.
     * M0 and M1 pins should be set to GND before calling this.
     *
     * @param rx_pin GPIO pin for UART RX (TXD of DX-LR01)
     * @param tx_pin GPIO pin for UART TX (RXD of DX-LR01)
     * @param baud Baud rate (default 9600 for DX-LR01)
     * @return true on success
     * @return false on failure
     */
    bool begin(int8_t rx_pin, int8_t tx_pin, uint32_t baud = 9600);

    /**
     * @brief Send a raw message over LoRa.
     *
     * @param msg Pointer to the byte buffer to send
     * @param size Number of bytes to send
     * @param is_nack If true, mark this message as a NACK (not used for DX-LR01)
     */
    void send_msg(byte* msg, byte size, bool is_nack = false);

    /**
     * @brief Send a null-terminated text string over LoRa.
     *
     * @param text C-string to send
     */
    void print(char* text);

    /**
     * @brief Install a callback table for message reception.
     *
     * @param functions Array of 256 function pointers (byte* msg, byte size)
     */
    void handle_callback(void (*functions[256])(byte* msg, byte size));

    /**
     * @brief Process incoming UART data (call regularly from loop).
     *
     * @return Number of bytes processed
     */
    int update();

    /**
     * @brief Get the last received message.
     *
     * @param out_size Output parameter for message size
     * @return Pointer to the received message buffer
     */
    byte* getLastMessage(int* out_size);

   private:
    HardwareSerial* loraSerial = nullptr;  // Serial2 for DX-LR01
    bool initialized = false;

    byte* buffer = new byte[256];  // RX buffer
    int buffer_index = 0;
    
    byte* last_received = new byte[256];  // Last received message
    int last_received_size = 0;  // Size of last received message

    void (*callbacks[256])(byte* msg, byte size) = {nullptr};  // Callback table
};

#endif
