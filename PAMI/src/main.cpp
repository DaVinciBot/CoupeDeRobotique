/*
#include <Arduino.h>
#include <SPI.h>
#include <RadioLib.h>

#define NSS 3
#define NRESET 2
#define DIO1 0
#define BUSY 1
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
*/
/*
#include <Arduino.h>
#include <SPI.h>
#include <RadioLib.h>

#define NSS 3
#define NRESET 2
#define DIO1 0
#define BUSY 1
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

  if (LoRa.setFrequency(868.0) != RADIOLIB_ERR_NONE) {
    Serial.println("Erreur de configuration de la fréquence!");
  }

  if (LoRa.setOutputPower(TX_POWER) != RADIOLIB_ERR_NONE) {
    Serial.println("Erreur de configuration de la puissance!");
  }

  if (LoRa.setSpreadingFactor(12) != RADIOLIB_ERR_NONE) {
    Serial.println("Erreur de configuration du SF!");
  }

  if (LoRa.setBandwidth(125.0) != RADIOLIB_ERR_NONE) {
    Serial.println("Erreur de configuration de la bande passante!");
  }

  Serial.println("Module SX1262 initialisé avec succès!");
}

void loop() {
  Serial.println("Envoi du message : Hello, LoRa!");
  int txStatus = LoRa.transmit("Hello, LoRa!");
  if (txStatus == RADIOLIB_ERR_NONE) {
    Serial.println("Message envoyé avec succès!");
  } else {
    Serial.println("Échec de l'envoi du message.");
  }

  delay(2000);

  Serial.println("Passage en mode réception...");
  String message;
  int rxStatus = LoRa.receive(message);
  if (rxStatus == RADIOLIB_ERR_NONE) {
    Serial.print("Message reçu : ");
    Serial.println(message);
  } else {
    Serial.println("Aucun message reçu.");
  }

  delay(5000);
}
*/
#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("✅ Setup started!");
}

void loop() {
  Serial.println("Loop is running...");
  delay(1000);
}
