#include <Arduino.h>
#include <com.h>
#include <crc.h>
#include <cstring>  // To use memcpy()

/**
 * @brief Constructor for USB serial communication.
 *
 * Initializes the communication stream for USB serial and sets up the internal
 * buffer.
 *
 * @param stream Pointer to the USB serial class.
 * @param baudrate Baud rate for serial communication.
 */
Com::Com(usb_serial_class* stream, uint32_t baudrate) {
    memcpy(this->signature, END_BYTES_SIGNATURE, sizeof(this->signature));

    this->stream = stream;
    stream->begin(baudrate);

    // Initialize the buffer
    for (uint16_t k = 0; k < 256; k++)
        this->buffer[k] = 0;
}

/**
 * @brief Constructor for hardware serial communication.
 *
 * Initializes the communication stream for hardware serial and sets up the
 * internal buffer.
 *
 * @param stream Pointer to the hardware serial class.
 * @param baudrate Baud rate for serial communication.
 */
Com::Com(HardwareSerial* stream, uint32_t baudrate) {
    this->stream = stream;
    stream->begin(baudrate);

    // Initialize the buffer
    for (uint16_t k = 0; k < 256; k++)
        this->buffer[k] = 0;
}

/**
 * @brief Handles incoming data from the communication stream.
 *
 * Processes incoming data byte by byte, checks for valid messages based on the
 * signature and CRC, and extracts the message size if a valid message is
 * detected.
 *
 * @return The size of the valid message, or 0 if no valid message is found.
 */
byte Com::handle() {
    while (this->stream->available()) {
        byte data = this->stream->read();
        this->buffer[this->pointer++] = data;

        // Wait until at least 6 bytes are received
        if (this->pointer < 6)
            continue;

        // Check for signature validity
        bool is_signature = true;
        for (int i = 0; i < 4 && is_signature; i++)
            is_signature =
                this->buffer[pointer - 1 - i] == this->signature[3 - i];

        if (!is_signature)
            continue;

        // Extract message size
        byte msg_size = this->buffer[pointer - 6];

        if (this->pointer >= msg_size + 6) {
            CRC crc;
            byte crc_b = crc.digest(this->buffer, msg_size + 1);

            // Validate CRC
            if (crc_b != this->buffer[msg_size + 1]) {
                byte invalid_crc_msg = NACK;
                send_msg(&invalid_crc_msg, 1);
                this->pointer = 0;
                continue;
            }

            // Reset the pointer and return the message size
            this->pointer = 0;
            return msg_size;
        } else {
            this->pointer = 0;
        }
    }
    return 0;
}

/**
 * @brief Handles callbacks for received messages.
 *
 * Processes received messages, retrieves the message ID, and calls the
 * corresponding callback function from the provided function array. Handles
 * unknown messages and retransmits the last message in case of NACK.
 *
 * @param functions Array of callback functions indexed by message ID.
 */
void Com::handle_callback(void (*functions[256])(byte* msg, byte size)) {
    // Retrieve the size of the received message
    byte size = this->handle();
    if (size > 0) {
        // Directly access the buffer pointer
        const byte* msg = this->read_buffer();
        if (msg == nullptr) {
            // Exit if the buffer is null (protection)
            return;
        }

        // Retrieve the message ID
        byte msg_id = msg[0];

        // Check if the function corresponding to the ID exists
        if (functions[msg_id] != nullptr) {
            functions[msg_id](const_cast<byte*>(msg),
                              size);  // Call the function
        } else if (msg_id == NACK) {
            // Resend the last message in case of NACK
            if (this->last_msg != nullptr) {
                this->send_msg((byte*)&this->last_msg->msg,
                               this->last_msg->size, true);
            }
        } else {
            // Handle unknown message types
            msg_unknown_msg_type error_message;
            error_message.type_id = msg_id;

            // Send a response indicating an unknown message type
            this->send_msg((byte*)&error_message, sizeof(msg_unknown_msg_type));
        }
    }
}

/**
 * @brief Provides access to the internal buffer.
 *
 * @return Pointer to the internal buffer.
 */
byte* Com::read_buffer() {
    return this->buffer;
}

/**
 * @brief Sends a message over the communication stream.
 *
 * Prepares the message with size and CRC, stores it as the last message (if not
 * a NACK), and sends it over the stream.
 *
 * @param msg Pointer to the message data to send.
 * @param size The size of the message data.
 * @param is_nack Indicates if the message is a retransmission due to a NACK.
 */
void Com::send_msg(byte* msg, byte size, bool is_nack) {
    if (!is_nack)
        free(this->last_msg);

    this->last_msg = new last_message();
    this->last_msg->size = size;

    CRC crc;

    // Prepare the full message with size and CRC
    byte* full_msg = new byte[size + 1];
    for (byte i = 0; i < size; i++) {
        full_msg[i] = msg[i];
        if (!is_nack)
            last_msg->msg[i] = msg[i];
    }
    full_msg[size] = size;

    // Compute CRC
    byte crc_b = crc.digest(full_msg, size + 1);

    // Send the message
    this->stream->write(msg, size);
    this->stream->write(size);
    this->stream->write(crc_b);
    this->stream->write(this->signature, 4);
    this->stream->flush();

    free(full_msg);
}

/**
 * @brief Sends a debug text message.
 *
 * This function sends a text message for debugging purposes. The message must
 * be in ASCII format and cannot exceed 253 characters.
 *
 * @param text Pointer to the null-terminated ASCII text string to send.
 */
void Com::print(char* text) {
    // Use send_msg to send the text input
    byte* msg = new byte[strlen(text) + 2];
    msg[0] = PRINT;
    for (byte i = 0; i <= strlen(text); i++) {
        msg[i + 1] = text[i];
    }
    this->send_msg(msg, strlen(msg) + 1);
    free(msg);
}
