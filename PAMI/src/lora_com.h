/*
#ifndef LORA_COM_H
#define LORA_COM_H

#include <Arduino.h>
#include <RadioLib.h>

class LoRaCom {
public:
    LoRaCom(int cs, int dio1, int reset, int busy);
    void initRadio();
    void sendPacket(const char* message);
    void receivePacket();
    bool isOperationDone();
    void resetOperationDone();
    bool isTransmitFlag();
    void resetTransmitFlag();
    int getTransmissionState();
    void startReceive();

    static void handleInterrupt();

private:
    SX1262 radio;
    volatile bool operationDone = false;
    bool transmitFlag = false;
    int transmissionState = RADIOLIB_ERR_NONE;

    bool validateParameters(float frequency, float bandwidth, uint8_t spreadingFactor, uint8_t codingRate, uint8_t syncWord, float outputPower, uint16_t preambleLength);
};

//byte Com::handle();
//void Com::handle_callback(void (*functions[256])(byte *msg, byte size));

#endif // LORA_COM_H
*/
/*
#ifndef LORA_COM_H
#define LORA_COM_H

#include <Arduino.h>
#include <RadioLib.h>
#include "crc.h"

// Définition de NACK
#define NACK 0xFF

struct Message {
    byte msg[256]; // Adjust size as needed
    byte size;
};

struct msg_unknown_msg_type {
    byte type_id;
    // Ajoute d'autres membres si nécessaire
};

class LoRaCom {
public:
    LoRaCom(int cs, int dio1, int reset, int busy);
    void initRadio();
    void sendPacket(const char* message);
    void receivePacket();
    bool isOperationDone();
    void resetOperationDone();
    bool isTransmitFlag();
    void resetTransmitFlag();
    int getTransmissionState();
    void startReceive();
    byte handle();
    void handle_callback(void (*functions[256])(byte *msg, byte size));

    static void handleInterrupt();

private:
    SX1262 radio;
    volatile bool operationDone = false;
    bool transmitFlag = false;
    int transmissionState = RADIOLIB_ERR_NONE;

    bool validateParameters(float frequency, float bandwidth, uint8_t spreadingFactor, uint8_t codingRate, uint8_t syncWord, float outputPower, uint16_t preambleLength);

    // Add necessary members for handle and handle_callback
    Stream* stream;
    byte* buffer;
    byte pointer = 0;
    byte signature[4];
    Message last_msg; // Utilise la structure Message

    const byte* read_buffer();
    void send_msg(byte *msg, byte size, bool is_retry = false);
};

#endif // LORA_COM_H
*/
#ifndef LORA_COM_H
#define LORA_COM_H

#include <Arduino.h>
#include <RadioLib.h>
#include "crc.h"

// Définition de NACK
#define NACK 0xFF
#define NUM_NODES 6

struct Message {
    byte msg[256]; // Adjust size as needed
    byte size;
};

struct msg_unknown_msg_type {
    byte type_id;
    // Ajoute d'autres membres si nécessaire
};

class LoRaCom {
public:
    LoRaCom(int cs, int dio1, int reset, int busy, byte node_id);
    void initRadio();
    void sendPacket(const char* message);
    void receivePacket();
    bool isOperationDone();
    void resetOperationDone();
    bool isTransmitFlag();
    void resetTransmitFlag();
    int getTransmissionState();
    void startReceive();
    byte handle();
    void handle_callback(void (*functions[256])(byte *msg, byte size));
    void send_msg(byte *msg, byte size, bool is_retry = false); // Rendre public

    static void handleInterrupt();

    Message received_msgs[NUM_NODES]; // Rendre public

private:
    SX1262 radio;
    volatile bool operationDone = false;
    bool transmitFlag = false;
    int transmissionState = RADIOLIB_ERR_NONE;
    byte node_id;

    bool validateParameters(float frequency, float bandwidth, uint8_t spreadingFactor, uint8_t codingRate, uint8_t syncWord, float outputPower, uint16_t preambleLength);

    // Add necessary members for handle and handle_callback
    Stream* stream;
    byte* buffer;
    byte pointer = 0;
    byte signature[4];
    Message last_msg; // Utilise la structure Message

    const byte* read_buffer();
};

#endif // LORA_COM_H
