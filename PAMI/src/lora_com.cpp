/*
#include "lora_com.h"
#include <modules/SX126x/patches/SX126x_patch_scan.h>

LoRaCom* LoRaComInstance;

LoRaCom::LoRaCom(int cs, int dio1, int reset, int busy)
    : radio(new Module(cs, dio1, reset, busy)) {
    LoRaComInstance = this;
}

void LoRaCom::handleInterrupt() {
    if (LoRaComInstance) {
        LoRaComInstance->operationDone = true;
    }
}

bool LoRaCom::validateParameters(float frequency, float bandwidth, uint8_t spreadingFactor, uint8_t codingRate, uint8_t syncWord, float outputPower, uint16_t preambleLength) {
    if (frequency < 150.0 || frequency > 960.0) {
        Serial.println(F("Error: Frequency must be between 150.0 MHz and 960.0 MHz."));
        return false;
    }
    if (bandwidth != 7.8 && bandwidth != 10.4 && bandwidth != 15.6 && bandwidth != 20.8 && bandwidth != 31.25 &&
        bandwidth != 41.7 && bandwidth != 62.5 && bandwidth != 125.0 && bandwidth != 250.0 && bandwidth != 500.0) {
        Serial.println(F("Error: Invalid bandwidth value."));
        return false;
    }
    if (spreadingFactor < 6 || spreadingFactor > 12) {
        Serial.println(F("Error: Spreading factor must be between 6 and 12."));
        return false;
    }
    if (codingRate < 5 || codingRate > 8) {
        Serial.println(F("Error: Coding rate must be between 5 and 8."));
        return false;
    }
    if (outputPower < -17.0 || outputPower > 22.0) {
        Serial.println(F("Error: Output power must be between -17 dBm and 22 dBm."));
        return false;
    }
    if (preambleLength < 6 || preambleLength > 65535) {
        Serial.println(F("Error: Preamble length must be between 6 and 65535 symbols."));
        return false;
    }
    if (syncWord > 0xFF) {
        Serial.println(F("Error: Sync word must be a valid 1-byte value."));
        return false;
    }
    return true;
}

void LoRaCom::initRadio() {
    float frequency = 915.0;
    float bandwidth = 125;
    uint8_t spreadingFactor = 7;
    uint8_t codingRate = 5;
    uint8_t syncWord = 0x12;
    float outputPower = 14;
    uint16_t preambleLength = 8;

    if (!validateParameters(frequency, bandwidth, spreadingFactor, codingRate, syncWord, outputPower, preambleLength)) {
        Serial.println(F("Error: Invalid parameters. Stopping."));
        while (true) { delay(10); }
    }

    Serial.print(F("[SX1262] Initializing ... "));
    int state = radio.begin(frequency, bandwidth, spreadingFactor, codingRate, syncWord, outputPower, preambleLength, 1.6, false);

    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("success!"));
        radio.setDio1Action(handleInterrupt);
    } else {
        Serial.print(F("failed, code "));
        Serial.println(state);
        while (true) { delay(10); }
    }
}

void LoRaCom::sendPacket(const char* message) {
    Serial.print(F("[SX1262] Sending packet ... "));
    transmissionState = radio.startTransmit(message);
    transmitFlag = true;
}

void LoRaCom::receivePacket() {
    String str;
    int state = radio.readData(str);
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("[SX1262] Received packet!"));
        Serial.print(F("[SX1262] Data: "));
        Serial.println(str);
        Serial.print(F("[SX1262] RSSI: "));
        Serial.print(radio.getRSSI());
        Serial.println(F(" dBm"));
        Serial.print(F("[SX1262] SNR: "));
        Serial.print(radio.getSNR());
        Serial.println(F(" dB"));
    } else {
        Serial.print(F("readData failed, code "));
        Serial.println(state);
    }
}

bool LoRaCom::isOperationDone() {
    return operationDone;
}

void LoRaCom::resetOperationDone() {
    operationDone = false;
}

bool LoRaCom::isTransmitFlag() {
    return transmitFlag;
}

void LoRaCom::resetTransmitFlag() {
    transmitFlag = false;
}

int LoRaCom::getTransmissionState() {
    return transmissionState;
}

void LoRaCom::startReceive() {
    radio.startReceive();
}
*/

/**
 * @brief Handles incoming data from the communication stream.
 *
 * Processes incoming data byte by byte, checks for valid messages based on the signature and CRC,
 * and extracts the message size if a valid message is detected.
 *
 * @return The size of the valid message, or 0 if no valid message is found.
 */
/*
byte Com::handle()
{
    while (this->stream->available())
    {
        byte data = this->stream->read();
        this->buffer[this->pointer++] = data;

        // Wait until at least 6 bytes are received
        if (this->pointer < 6)
            continue;

        // Check for signature validity
        bool is_signature = true;
        for (int i = 0; i < 4 && is_signature; i++)
            is_signature = this->buffer[pointer - 1 - i] == this->signature[3 - i];

        if (!is_signature)
            continue;

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
                continue;
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
*/
/**
 * @brief Handles callbacks for received messages.
 *
 * Processes received messages, retrieves the message ID, and calls the corresponding callback function
 * from the provided function array. Handles unknown messages and retransmits the last message in case of NACK.
 *
 * @param functions Array of callback functions indexed by message ID.
 */
/*
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
*/
//THE GOOD ONE
#include "lora_com.h"
#include <modules/SX126x/patches/SX126x_patch_scan.h>
#include <crc.h>

LoRaCom* LoRaComInstance;

LoRaCom::LoRaCom(int cs, int dio1, int reset, int busy)
    : radio(new Module(cs, dio1, reset, busy)), stream(&Serial) {
    LoRaComInstance = this;
    // Initialize buffer and signature
    buffer = new byte[256]; // Adjust size as needed
    signature[0] = 0xDE; // Example signature, adjust as needed
    signature[1] = 0xAD;
    signature[2] = 0xBE;
    signature[3] = 0xEF;
}

void LoRaCom::handleInterrupt() {
    if (LoRaComInstance) {
        LoRaComInstance->operationDone = true;
    }
}

bool LoRaCom::validateParameters(float frequency, float bandwidth, uint8_t spreadingFactor, uint8_t codingRate, uint8_t syncWord, float outputPower, uint16_t preambleLength) {
    if (frequency < 150.0 || frequency > 960.0) {
        Serial.println(F("Error: Frequency must be between 150.0 MHz and 960.0 MHz."));
        return false;
    }
    if (bandwidth != 7.8 && bandwidth != 10.4 && bandwidth != 15.6 && bandwidth != 20.8 && bandwidth != 31.25 &&
        bandwidth != 41.7 && bandwidth != 62.5 && bandwidth != 125.0 && bandwidth != 250.0 && bandwidth != 500.0) {
        Serial.println(F("Error: Invalid bandwidth value."));
        return false;
    }
    if (spreadingFactor < 6 || spreadingFactor > 12) {
        Serial.println(F("Error: Spreading factor must be between 6 and 12."));
        return false;
    }
    if (codingRate < 5 || codingRate > 8) {
        Serial.println(F("Error: Coding rate must be between 5 and 8."));
        return false;
    }
    if (outputPower < -17.0 || outputPower > 22.0) {
        Serial.println(F("Error: Output power must be between -17 dBm and 22 dBm."));
        return false;
    }
    if (preambleLength < 6 || preambleLength > 65535) {
        Serial.println(F("Error: Preamble length must be between 6 and 65535 symbols."));
        return false;
    }
    if (syncWord > 0xFF) {
        Serial.println(F("Error: Sync word must be a valid 1-byte value."));
        return false;
    }
    return true;
}

void LoRaCom::initRadio() {
    float frequency = 915.0;
    float bandwidth = 125;
    uint8_t spreadingFactor = 7;
    uint8_t codingRate = 5;
    uint8_t syncWord = 0x12;
    float outputPower = 14;
    uint16_t preambleLength = 8;

    if (!validateParameters(frequency, bandwidth, spreadingFactor, codingRate, syncWord, outputPower, preambleLength)) {
        Serial.println(F("Error: Invalid parameters. Stopping."));
        while (true) { delay(10); }
    }

    Serial.print(F("[SX1262] Initializing ... "));
    int state = radio.begin(frequency, bandwidth, spreadingFactor, codingRate, syncWord, outputPower, preambleLength, 1.6, false);

    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("success!"));
        radio.setDio1Action(handleInterrupt);
    } else {
        Serial.print(F("failed, code "));
        Serial.println(state);
        while (true) { delay(10); }
    }
}

void LoRaCom::sendPacket(const char* message) {
    Serial.print(F("[SX1262] Sending packet ... "));
    transmissionState = radio.startTransmit(message);
    transmitFlag = true;
}

void LoRaCom::receivePacket() {
    String str;
    int state = radio.readData(str);
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("[SX1262] Received packet!"));
        Serial.print(F("[SX1262] Data: "));
        Serial.println(str);
        Serial.print(F("[SX1262] RSSI: "));
        Serial.print(radio.getRSSI());
        Serial.println(F(" dBm"));
        Serial.print(F("[SX1262] SNR: "));
        Serial.print(radio.getSNR());
        Serial.println(F(" dB"));
    } else {
        Serial.print(F("readData failed, code "));
        Serial.println(state);
    }
}

bool LoRaCom::isOperationDone() {
    return operationDone;
}

void LoRaCom::resetOperationDone() {
    operationDone = false;
}

bool LoRaCom::isTransmitFlag() {
    return transmitFlag;
}

void LoRaCom::resetTransmitFlag() {
    transmitFlag = false;
}

int LoRaCom::getTransmissionState() {
    return transmissionState;
}

void LoRaCom::startReceive() {
    radio.startReceive();
}
byte LoRaCom::handle() {
    if (stream == nullptr) {
        Serial.println(F("Error: Stream is not initialized"));
        return 0;
    }
    Serial.println(F("Handle method called"));
    while (this->stream->available()) {
        byte data = this->stream->read();
        this->buffer[this->pointer++] = data;

        // Wait until at least 6 bytes are received
        if (this->pointer < 6)
            continue;

        // Check for signature validity
        bool is_signature = true;
        for (int i = 0; i < 4 && is_signature; i++)
            is_signature = this->buffer[pointer - 1 - i] == this->signature[3 - i];

        if (!is_signature)
            continue;

        // Extract message size
        byte msg_size = this->buffer[pointer - 6];
        Serial.print(F("Message size extracted: "));
        Serial.println(msg_size);

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
            Serial.println(F("Message received and validated"));
            return msg_size;
        } else {
            this->pointer = 0;
        }
    }
    return 0;
}

/*
byte LoRaCom::handle() {
    if (stream == nullptr) {
        Serial.println(F("Error: Stream is not initialized"));
        return 0;
    }
    Serial.println(F("Handle method called"));
    while (this->stream->available()) {
        byte data = this->stream->read();
        this->buffer[this->pointer++] = data;

        // Wait until at least 6 bytes are received
        if (this->pointer < 6)
            continue;

        // Check for signature validity
        bool is_signature = true;
        for (int i = 0; i < 4 && is_signature; i++)
            is_signature = this->buffer[pointer - 1 - i] == this->signature[3 - i];

        if (!is_signature)
            continue;

        // Extract message size
        byte msg_size = this->buffer[pointer - 6];
        Serial.print(F("Message size extracted: "));
        Serial.println(msg_size);

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
            Serial.println(F("Message received and validated"));
            return msg_size;
        } else {
            this->pointer = 0;
        }
    }
    return 0;
}
*/

void LoRaCom::handle_callback(void (*functions[256])(byte *msg, byte size)) {
    Serial.println(F("Handle_callback method called"));
    // Retrieve the size of the received message
    byte size = this->handle();
    if (size > 0) {
        // Directly access the buffer pointer
        const byte *msg = this->read_buffer();
        if (msg == nullptr) {
            // Exit if the buffer is null (protection)
            return;
        }

        // Retrieve the message ID
        byte msg_id = msg[0];
        if (functions[msg_id] != nullptr) {
            Serial.print(F("Calling callback for message ID: "));
            Serial.println(msg_id);
            functions[msg_id](const_cast<byte *>(msg), size); // Call the function
        } else if (msg_id == NACK) {
            // Resend the last message in case of NACK
            Serial.println(F("NACK received, resending last message"));
            if (this->last_msg.size > 0) {
                this->send_msg(this->last_msg.msg, this->last_msg.size, true);
            }
        } else {
            // Handle unknown message types
            Serial.print(F("Unknown message type: "));
            Serial.println(msg_id);
            msg_unknown_msg_type error_message;
            error_message.type_id = msg_id;

            // Send a response indicating an unknown message type
            this->send_msg((byte *)&error_message, sizeof(msg_unknown_msg_type));
        }
    }
}

const byte* LoRaCom::read_buffer() {
    // Implement this method to return the buffer pointer
    return this->buffer;
}

void LoRaCom::send_msg(byte *msg, byte size, bool is_retry) {
    // Implement this method to send a message
    // For example, you can use radio.startTransmit(msg, size);
    if (is_retry) {
        // Handle retry logic if needed
    }
    radio.startTransmit(msg, size);
}

/*
#include "lora_com.h"
#include <modules/SX126x/patches/SX126x_patch_scan.h>
#include "crc.h"

LoRaCom* LoRaComInstance;

LoRaCom::LoRaCom(int cs, int dio1, int reset, int busy, byte node_id)
    : radio(new Module(cs, dio1, reset, busy)), stream(&Serial), node_id(node_id) {
    LoRaComInstance = this;
    // Initialize buffer and signature
    buffer = new byte[256]; // Adjust size as needed
    signature[0] = 0xDE; // Example signature, adjust as needed
    signature[1] = 0xAD;
    signature[2] = 0xBE;
    signature[3] = 0xEF;
    // Initialize received messages array
    for (int i = 0; i < NUM_NODES; i++) {
        received_msgs[i].size = 0;
    }
}

void LoRaCom::handleInterrupt() {
    if (LoRaComInstance) {
        LoRaComInstance->operationDone = true;
    }
}

bool LoRaCom::validateParameters(float frequency, float bandwidth, uint8_t spreadingFactor, uint8_t codingRate, uint8_t syncWord, float outputPower, uint16_t preambleLength) {
    if (frequency < 150.0 || frequency > 960.0) {
        Serial.println(F("Error: Frequency must be between 150.0 MHz and 960.0 MHz."));
        return false;
    }
    if (bandwidth != 7.8 && bandwidth != 10.4 && bandwidth != 15.6 && bandwidth != 20.8 && bandwidth != 31.25 &&
        bandwidth != 41.7 && bandwidth != 62.5 && bandwidth != 125.0 && bandwidth != 250.0 && bandwidth != 500.0) {
        Serial.println(F("Error: Invalid bandwidth value."));
        return false;
    }
    if (spreadingFactor < 6 || spreadingFactor > 12) {
        Serial.println(F("Error: Spreading factor must be between 6 and 12."));
        return false;
    }
    if (codingRate < 5 || codingRate > 8) {
        Serial.println(F("Error: Coding rate must be between 5 and 8."));
        return false;
    }
    if (outputPower < -17.0 || outputPower > 22.0) {
        Serial.println(F("Error: Output power must be between -17 dBm and 22 dBm."));
        return false;
    }
    if (preambleLength < 6 || preambleLength > 65535) {
        Serial.println(F("Error: Preamble length must be between 6 and 65535 symbols."));
        return false;
    }
    if (syncWord > 0xFF) {
        Serial.println(F("Error: Sync word must be a valid 1-byte value."));
        return false;
    }
    return true;
}

void LoRaCom::initRadio() {
    float frequency = 915.0;
    float bandwidth = 125;
    uint8_t spreadingFactor = 7;
    uint8_t codingRate = 5;
    uint8_t syncWord = 0x12;
    float outputPower = 14;
    uint16_t preambleLength = 8;

    if (!validateParameters(frequency, bandwidth, spreadingFactor, codingRate, syncWord, outputPower, preambleLength)) {
        Serial.println(F("Error: Invalid parameters. Stopping."));
        while (true) { delay(10); }
    }

    Serial.print(F("[SX1262] Initializing ... "));
    int state = radio.begin(frequency, bandwidth, spreadingFactor, codingRate, syncWord, outputPower, preambleLength, 1.6, false);

    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("success!"));
        radio.setDio1Action(handleInterrupt);
    } else {
        Serial.print(F("failed, code "));
        Serial.println(state);
        while (true) { delay(10); }
    }
}

void LoRaCom::sendPacket(const char* message) {
    Serial.print(F("[SX1262] Sending packet ... "));
    transmissionState = radio.startTransmit(message);
    transmitFlag = true;
}

void LoRaCom::receivePacket() {
    String str;
    int state = radio.readData(str);
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("[SX1262] Received packet!"));
        Serial.print(F("[SX1262] Data: "));
        Serial.println(str);
        Serial.print(F("[SX1262] RSSI: "));
        Serial.print(radio.getRSSI());
        Serial.println(F(" dBm"));
        Serial.print(F("[SX1262] SNR: "));
        Serial.print(radio.getSNR());
        Serial.println(F(" dB"));
    } else {
        Serial.print(F("readData failed, code "));
        Serial.println(state);
    }
}

bool LoRaCom::isOperationDone() {
    return operationDone;
}

void LoRaCom::resetOperationDone() {
    operationDone = false;
}

bool LoRaCom::isTransmitFlag() {
    return transmitFlag;
}

void LoRaCom::resetTransmitFlag() {
    transmitFlag = false;
}

int LoRaCom::getTransmissionState() {
    return transmissionState;
}

void LoRaCom::startReceive() {
    radio.startReceive();
}

byte LoRaCom::handle() {
    if (stream == nullptr) {
        Serial.println(F("Error: Stream is not initialized"));
        return 0;
    }
    Serial.println(F("Handle method called"));
    while (this->stream->available()) {
        byte data = this->stream->read();
        this->buffer[this->pointer++] = data;

        // Wait until at least 6 bytes are received
        if (this->pointer < 6)
            continue;

        // Check for signature validity
        bool is_signature = true;
        for (int i = 0; i < 4 && is_signature; i++)
            is_signature = this->buffer[pointer - 1 - i] == this->signature[3 - i];

        if (!is_signature)
            continue;

        // Extract message size
        byte msg_size = this->buffer[pointer - 6];
        Serial.print(F("Message size extracted: "));
        Serial.println(msg_size);

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
            Serial.println(F("Message received and validated"));
            return msg_size;
        } else {
            this->pointer = 0;
        }
    }
    return 0;
}

void LoRaCom::handle_callback(void (*functions[256])(byte *msg, byte size)) {
    Serial.println(F("Handle_callback method called"));
    // Retrieve the size of the received message
    byte size = this->handle();
    if (size > 0) {
        // Directly access the buffer pointer
        const byte *msg = this->read_buffer();
        if (msg == nullptr) {
            // Exit if the buffer is null (protection)
            return;
        }

        // Retrieve the message ID
        byte msg_id = msg[0];
        if (msg_id < NUM_NODES && msg_id != node_id) {
            // Store the message in the corresponding slot
            memcpy(received_msgs[msg_id].msg, msg, size);
            received_msgs[msg_id].size = size;
            Serial.print(F("Stored message from node: "));
            Serial.println(msg_id);
        }

        // Resend the last message in case of NACK
        if (msg_id == NACK) {
            Serial.println(F("NACK received, resending last message"));
            if (this->last_msg.size > 0) {
                this->send_msg(this->last_msg.msg, this->last_msg.size, true);
            }
        }

        // Call the function if it exists
        if (functions[msg_id] != nullptr) {
            Serial.print(F("Calling callback for message ID: "));
            Serial.println(msg_id);
            functions[msg_id](const_cast<byte *>(msg), size); // Call the function
        }
    }
}

const byte* LoRaCom::read_buffer() {
    // Implement this method to return the buffer pointer
    return this->buffer;
}

void LoRaCom::send_msg(byte *msg, byte size, bool is_retry) {
    // Implement this method to send a message
    // For example, you can use radio.startTransmit(msg, size);
    if (is_retry) {
        // Handle retry logic if needed
    }
    radio.startTransmit(msg, size);
}
*/