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

byte Com::handle();
void Com::handle_callback(void (*functions[256])(byte *msg, byte size));

#endif // LORA_COM_H
