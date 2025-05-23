#include <com.h>

Com::Com()
{
    memcpy(this->signature, END_BYTES_SIGNATURE, sizeof(this->signature));

    // Initialize the buffer
    for (uint16_t k = 0; k < 256; k++)
        this->buffer[k] = 0;
}

Com::~Com()
{
}

bool Com::begin(int8_t nss, int8_t reset, int8_t busy)
{
    // Begin LoRa radio and set NSS, reset, busy, txen, and rxen pin with connected Arduino pins
    Serial.println("Begin LoRa radio");
    if (!LoRa.begin(nss, reset, busy))
    {
        Serial.println("Something wrong, can't begin LoRa radio");
        return false;
    }

    Serial.println("Set frequency to 915 MHz");
    LoRa.setFrequency(915000000);

    Serial.println("Set TX power to +17 dBm");
    LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);

    Serial.println("Set modulation parameters");
    LoRa.setLoRaModulation(sf, bw, cr);

    Serial.println("Set packet parameters");
    LoRa.setLoRaPacket(headerType, preambleLength, message_len, crcType);

    Serial.println("Set synchronize word");
    LoRa.setSyncWord(syncWord);

    Serial.println("\n-- LORA TRANSMITTER / RECEIVER --\n");
    return true;
}

byte Com::handle()
{
    while (LoRa.available())
    {
        byte data = LoRa.read();
        this->buffer[this->pointer++] = data;

        // Wait until at least 6 bytes are received
        if (this->pointer < 6)
            break;

        // Check for signature validity
        bool is_signature = true;
        for (int i = 0; i < 4 && is_signature; i++)
            is_signature = this->buffer[pointer - 1 - i] == this->signature[3 - i];

        if (!is_signature)
            break;

        // Extract message size
        byte msg_size = this->buffer[pointer - 6];

        if (this->pointer >= msg_size + 6)
        {
            CRC crc;
            byte crc_b = crc.digest(this->buffer, msg_size + 1);

            // Validate CRC
            if (crc_b != this->buffer[msg_size + 1])
            {
                byte invalid_crc_msg = NACK;
                send_msg(&invalid_crc_msg, 1);
                this->pointer = 0;
                break;
            }

            // Reset the pointer and return the message size
            this->pointer = 0;
            return msg_size;
        }
        else
        {
            this->pointer = 0;
        }
    }
    return 0;
}

void Com::handle_callback(void (*functions[256])(byte *msg, byte size))
{
    // Retrieve the size of the received message
    byte size = this->handle();
    if (size > 0)
    {
        // Directly access the buffer pointer
        const byte *msg = this->read_buffer();
        if (msg == nullptr)
        {
            // Exit if the buffer is null (protection)
            return;
        }

        // Retrieve the message ID
        byte msg_id = msg[0];

        // Check if the function corresponding to the ID exists
        if (functions[msg_id] != nullptr)
        {
            functions[msg_id](const_cast<byte *>(msg), size); // Call the function
        }
        else if (msg_id == NACK)
        {
            // Resend the last message in case of NACK
            if (this->last_msg != nullptr)
            {
                this->send_msg((byte *)&this->last_msg->msg, this->last_msg->size, true);
            }
        }
        else
        {
            // Handle unknown message types
            msg_unknown_msg_type error_message;
            error_message.type_id = msg_id;

            // Send a response indicating an unknown message type
            this->send_msg((byte *)&error_message, sizeof(msg_unknown_msg_type));
        }
    }
}

/**
 * @brief Provides access to the internal buffer.
 *
 * @return Pointer to the internal buffer.
 */
byte *Com::read_buffer()
{
    return this->buffer;
}

void Com::send_msg(byte *msg, byte size, bool is_nack)
{
    if (!is_nack)
        free(this->last_msg);

    this->last_msg = new last_message();
    this->last_msg->size = size;

    CRC crc;

    // Prepare the full message with size and CRC
    byte *full_msg = new byte[size + 1];
    for (byte i = 0; i < size; i++)
    {
        full_msg[i] = msg[i];
        if (!is_nack)
            last_msg->msg[i] = msg[i];
    }
    full_msg[size] = size;

    // Compute CRC
    byte crc_b = crc.digest(full_msg, size + 1);

    // Send the message
    LoRa.beginPacket();
    LoRa.write(full_msg, size + 1);
    LoRa.write(crc_b);
    LoRa.write(this->signature, 4);
    LoRa.endPacket();
    LoRa.wait();

    free(full_msg);
    LoRa.request(); // Request for receiving new LoRa packet
}

void Com::print(char *text)
{
    // Use send_msg to send the text input
    byte *msg = new byte[strlen(text) + 2];
    msg[0] = PRINT;
    for (byte i = 0; i <= strlen(text); i++)
    {
        msg[i + 1] = text[i];
    }
    this->send_msg(msg, strlen(text) + 3);
    free(msg);
}