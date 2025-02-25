#include <Arduino.h>
#include <SPI.h>
#include <RadioLib.h>

#define NSS 10
#define NRESET 9
#define DIO1 8
#define BUSY 7
#define TX_POWER 13

SX1262 LoRa = new Module(NSS, DIO1, NRESET, BUSY);

void setup() {
  Serial.begin(115200);
  while (!Serial);
  
  Serial.println("Initialisation du module LoRa SX1262...");
  if (LoRa.begin() != RADIOLIB_ERR_NONE) {
    Serial.println("Erreur d'initialisation du module LoRa!");
    while (1);
  }
  
  LoRa.setFrequency(868.0);
  LoRa.setOutputPower(TX_POWER);
  LoRa.setSpreadingFactor(12);
  LoRa.setBandwidth(125.0);
  Serial.println("Module SX1262 initialisé avec succès!");
}

void loop() {
  // First, send a message
  Serial.println("Envoi du message : Hello, LoRa!");
  if (LoRa.transmit("Hello, LoRa!") == RADIOLIB_ERR_NONE) {
    Serial.println("Message envoyé avec succès!");
  } else {
    Serial.println("Échec de l'envoi du message.");
  }
  
  // Allow some time for the other device to transmit
  delay(2000);

  // Then try receiving any message
  Serial.println("Passage en mode réception...");
  String message;
  int state = LoRa.receive(message);
  if (state == RADIOLIB_ERR_NONE) {
    Serial.print("Message reçu : ");
    Serial.println(message);
  } else {
    Serial.println("Aucun message reçu.");
  }
  
  // Wait before starting next cycle
  delay(5000);
}
