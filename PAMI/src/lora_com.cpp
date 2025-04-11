#include "lora_com.h"
#include <Arduino.h>
#include <RadioLib.h>
#include <modules/SX126x/patches/SX126x_patch_scan.h>

/*
  LoRa Communication Main Program using Handlers

  This sketch demonstrates how to handle events using dedicated handlers.
  When a message is received, the receive handler is called, and it automatically sends
  the fixed message "je suis pas la".
*/

#include "lora_com.h"

// Create a global instance of the lora_com class.
lora_com lora;

// Handler called when a message is received.
void handleReceive(String message) {
  Serial.print("Handler - Received: ");
  Serial.println(message);
  // Send the fixed message "je suis pas la" after receiving a message.
  lora.sendPacket("je suis pas la");
}

// Handler called when a transmission completes.
void handleTransmit(int state) {
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("Handler - Transmission succeeded!");
  } else {
    Serial.print("Handler - Transmission error, state: ");
    Serial.println(state);
  }
}

void setup() {
  // Initialize serial communication for verification.
  Serial.begin(115200);
  while (!Serial);  // Wait for the serial port to be ready
  
  // Register the event handlers.
  lora.setReceiveHandler(handleReceive);
  lora.setTransmitHandler(handleTransmit);

  // Initialize the LoRa radio.
  lora.begin();
}

void loop() {
  // Continuously update the LoRa module; the handler functions will be
  // called automatically when events (transmission or reception) occur.
  lora.update();
  delay(10);
}
