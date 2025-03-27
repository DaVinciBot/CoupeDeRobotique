#ifndef LORA_COM_H
#define LORA_COM_H

#pragma once

#include <Arduino.h>
#include <RadioLib.h>
#include <modules/SX126x/patches/SX126x_patch_scan.h>

// Pin definitions
#define LORA_MISO   8    // confirmed
#define LORA_SCK    7    // confirmed
#define LORA_MOSI   9    // confirmed
#define LORA_CS     41   // NSS
#define LORA_DIO2   38
#define LORA_DIO1   39   // irq
#define LORA_RESET  42
#define LORA_BUSY   40

// Uncomment if this node should initiate the communication
#define INITIATING_NODE

class lora_com {
public:
  lora_com();
  
  // Initializes the radio module and, if INITIATING_NODE is defined, sends the first packet.
  void begin();
  
  // Should be called repeatedly (e.g. in Arduino loop()) to handle asynchronous events.
  void update();

  // Sends a packet with the provided message.
  void sendPacket(const char* message);

private:
  // Static callback to set the operation flag (called by the radio library interrupt)
  static void dio1Callback();
  
  // Validates radio parameters before initialization.
  bool validateParameters(float frequency, float bandwidth, uint8_t spreadingFactor,
                          uint8_t codingRate, uint8_t syncWord, float outputPower, uint16_t preambleLength);
  
  // Initializes the radio with given parameters.
  void initRadio();
  
  // Receives and prints incoming packet data.
  void receivePacket();

  // Static pointer to hold the single instance (to be used in the callback)
  static lora_com* instance;

  // RadioLib SX1262 object constructed with the pin definitions.
  SX1262 radio;

  // Flags to handle asynchronous transmit/receive events.
  volatile bool operationDone;
  bool transmitFlag;
  int transmissionState;
};

// Define the static instance pointer.
lora_com* lora_com::instance = nullptr;

// Constructor: Initialize member variables and assign the instance pointer.
lora_com::lora_com()
  : radio(LORA_CS, LORA_DIO1, LORA_RESET, LORA_BUSY),
    operationDone(false),
    transmitFlag(false),
    transmissionState(RADIOLIB_ERR_NONE)
{
  instance = this;
}

// Validate the parameters. If any parameter is out of its valid range, print an error and return false.
bool lora_com::validateParameters(float frequency, float bandwidth, uint8_t spreadingFactor,
                                  uint8_t codingRate, uint8_t syncWord, float outputPower, uint16_t preambleLength) {
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

// Initialize the radio by setting up the parameters, validating them, and calling the radio library begin() function.
void lora_com::initRadio() {
  float frequency = 915.0;
  float bandwidth = 125.0;
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
    // Set the interrupt callback for DIO1.
    radio.setDio1Action(dio1Callback);
  } else {
    Serial.print(F("failed, code "));
    Serial.println(state);
    while (true) { delay(10); }
  }
}

// Begin the radio by initializing it and either sending the first packet (if INITIATING_NODE is defined) or starting receive mode.
void lora_com::begin() {
  initRadio();
  #ifdef INITIATING_NODE
    sendPacket("234576");
  #else
    radio.startReceive();
  #endif
}

// Send a packet. This function starts the transmission and sets the transmit flag.
void lora_com::sendPacket(const char* message) {
  Serial.print(F("[SX1262] Sending packet ... "));
  transmissionState = radio.startTransmit(message);
  transmitFlag = true;
}

// Receive a packet and print its data, RSSI, and SNR.
void lora_com::receivePacket() {
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

// This update() method is intended to be called repeatedly (e.g., from the Arduino loop).
// It checks if an interrupt has signaled that an operation is done and then handles transmission or reception accordingly.
void lora_com::update() {
  if (operationDone) {
    operationDone = false;
    if (transmitFlag) {
      if (transmissionState == RADIOLIB_ERR_NONE) {
        Serial.println(F("transmission finished!"));
      } else {
        Serial.print(F("failed, code "));
        Serial.println(transmissionState);
      }
      radio.startReceive();
      transmitFlag = false;
    } else {
      receivePacket();
      delay(5000);
      sendPacket("Pikachu!");
    }
  }
}

// Static callback function for DIO1 interrupt. It simply sets the operationDone flag in the instance.
void lora_com::dio1Callback() {
  if (instance) {
    instance->operationDone = true;
  }
}




#endif