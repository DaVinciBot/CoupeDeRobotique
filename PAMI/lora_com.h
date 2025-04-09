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

  // Must be called repeatedly (e.g., in Arduino loop()) to handle asynchronous events.
  void update();

  // Sends a packet with the provided message.
  void sendPacket(const char* message);

  // Registration for event handlers:
  // Handler to be called on message reception.
  void setReceiveHandler(void (*handler)(String));
  // Handler to be called on transmission completion.
  // The handler receives an int status (0 for success, nonzero for error code).
  void setTransmitHandler(void (*handler)(int));

private:
  // Static callback to set the operation flag (called by the radio library interrupt)
  static void dio1Callback();

  // Validates radio parameters before initialization.
  bool validateParameters(float frequency, float bandwidth, uint8_t spreadingFactor,
                          uint8_t codingRate, uint8_t syncWord, float outputPower, uint16_t preambleLength);

  // Initializes the radio with given parameters.
  void initRadio();

  // Receives the incoming packet and stores the data.
  void receivePacket();

  // Static pointer to hold the single instance (to be used in the callback).
  static lora_com* instance;

  // RadioLib SX1262 object constructed with the pin definitions.
  SX1262 radio;

  // Flags to handle asynchronous events.
  volatile bool operationDone;
  bool transmitFlag;
  int transmissionState;

  // Storage for the last received message.
  String receivedMessage;
  bool messageReady;

  // Handler function pointers.
  void (*onReceiveHandler)(String);
  void (*onTransmitHandler)(int);
};

// Define the static instance pointer.
lora_com* lora_com::instance = nullptr;

// Constructor: Initialize member variables and assign the instance pointer.
lora_com::lora_com()
  : radio(LORA_CS, LORA_DIO1, LORA_RESET, LORA_BUSY),
    operationDone(false),
    transmitFlag(false),
    transmissionState(RADIOLIB_ERR_NONE),
    receivedMessage(""),
    messageReady(false),
    onReceiveHandler(nullptr),
    onTransmitHandler(nullptr)
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

// Begin the radio by initializing it.
// If INITIATING_NODE is defined, the begin() function sends a preset message.
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

// Receive a packet and store its data.
void lora_com::receivePacket() {
  String str;
  int state = radio.readData(str);
  if (state == RADIOLIB_ERR_NONE) {
    receivedMessage = str;
    messageReady = true;
  } else {
    Serial.print(F("readData failed, code "));
    Serial.println(state);
  }
}

// The update() method checks if an asynchronous operation has completed,
// then calls the appropriate handler if one is registered.
void lora_com::update() {
  if (operationDone) {
    operationDone = false;
    if (transmitFlag) {
      if (transmissionState == RADIOLIB_ERR_NONE) {
        Serial.println(F("[SX1262] Transmission finished!"));
        if (onTransmitHandler) {
          onTransmitHandler(RADIOLIB_ERR_NONE);
        }
      } else {
        Serial.print(F("[SX1262] Transmission failed, code "));
        Serial.println(transmissionState);
        if (onTransmitHandler) {
          onTransmitHandler(transmissionState);
        }
      }
      radio.startReceive();
      transmitFlag = false;
    } else {
      // Reception event
      receivePacket();
      if (messageReady && onReceiveHandler) {
        onReceiveHandler(receivedMessage);
        // Clear the flag after calling the handler.
        messageReady = false;
      }
    }
  }
}

// Static callback function for DIO1 interrupt.
// It sets the operationDone flag for the current instance.
void lora_com::dio1Callback() {
  if (instance) {
    instance->operationDone = true;
  }
}

// Register a function to handle received messages.
void lora_com::setReceiveHandler(void (*handler)(String)) {
  onReceiveHandler = handler;
}

// Register a function to handle transmission completion events.
void lora_com::setTransmitHandler(void (*handler)(int)) {
  onTransmitHandler = handler;
}

#endif
