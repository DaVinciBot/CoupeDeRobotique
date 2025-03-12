// #include "OTA.h"
// AsyncWebServer server(80);
// CustomOTA ota("DVB_CDR", "davincibot", &server);
//#include <Arduino.h>
//#include <SPI.h>
//#include <RadioLib.h>
//#include <BaseLoRa.h>
//#include <SX126x.h>

#include <Arduino.h>
#include <SPI.h>
#include <BaseLoRa.h>
#include <SX126x.h>

SX126x LoRa;

// Message à transmettre
char message[] = "HeLoRa World!";
uint8_t nBytes = sizeof(message);
uint8_t counter = 0;

void setup() {
  Serial.begin(38400);
  
  // Initialisation du module LoRa avec les pins définies
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)) {
    Serial.println("Erreur d'initialisation de la radio LoRa");
    while (1);
  }
  
  // Configuration de la fréquence, puissance, modulation et paquet
  LoRa.setFrequency(915000000);
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);
  uint8_t sf = 7;
  uint32_t bw = 125000;
  uint8_t cr = 5;
  LoRa.setLoRaModulation(sf, bw, cr);
  
  uint8_t headerType = SX126X_HEADER_EXPLICIT;
  uint16_t preambleLength = 12;
  uint8_t payloadLength = 15;  // 14 octets pour le message + 1 octet pour le compteur
  bool crcType = true;
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);
  
  LoRa.setSyncWord(0x3444);
  
  Serial.println("Transmetteur LoRa initialisé");
}

void loop() {
  // Préparer et envoyer le paquet (message + compteur)
  LoRa.beginPacket();
  LoRa.write(message, nBytes);
  LoRa.write(counter);
  LoRa.endPacket();
  
  // Affichage sur le moniteur série
  Serial.print("Transmitted: ");
  Serial.print(message);
  Serial.print("  ");
  Serial.println(counter++);
  
  Serial.print("Transmit time: ");
  Serial.print(LoRa.transmitTime());
  Serial.println(" ms");
  
  delay(1000);  // Délai entre chaque transmission
}

/*

#include <Arduino.h>
#include <SPI.h>
#include <BaseLoRa.h>
#include <SX126x.h>

SX126x LoRa;

void setup() {
  Serial.begin(38400);
  
  // Initialisation du module LoRa avec les pins définies
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)) {
    Serial.println("Erreur d'initialisation de la radio LoRa");
    while (1);
  }
  
  // Configuration de la fréquence, puissance, modulation et paquet
  LoRa.setFrequency(915000000);
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);
  uint8_t sf = 7;
  uint32_t bw = 125000;
  uint8_t cr = 5;
  LoRa.setLoRaModulation(sf, bw, cr);
  
  uint8_t headerType = SX126X_HEADER_EXPLICIT;
  uint16_t preambleLength = 12;
  uint8_t payloadLength = 15;  // 14 octets pour le message + 1 octet pour le compteur
  bool crcType = true;
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);
  
  LoRa.setSyncWord(0x3444);
  
  Serial.println("Récepteur LoRa initialisé");
}

void loop() {
  // Passage en mode réception
  LoRa.request();
  LoRa.wait();
  
  // Vérification qu'il y a au moins un octet (le message + le compteur)
  if (LoRa.available() > 0) {
    // Le dernier octet est supposé être le compteur, on calcule donc la longueur du message
    const uint8_t msgLen = LoRa.available() - 1;
    if (msgLen > 0) {
      char receivedMessage[msgLen + 1];  // +1 pour le caractère nul de fin
      uint8_t receivedCounter;
      uint8_t i = 0;
      
      // Lecture de tous les octets sauf le dernier
      while (LoRa.available() > 1) {
        receivedMessage[i++] = LoRa.read();
      }
      
      // Terminer la chaîne
      receivedMessage[i] = '\0';
      
      // Lecture du dernier octet (le compteur)
      receivedCounter = LoRa.read();
      
      // Affichage du message et du compteur
      Serial.print("Received: ");
      Serial.print(receivedMessage);
      Serial.print("  ");
      Serial.println(receivedCounter);
      
      // Affichage des informations de signal
      Serial.print("Packet status: RSSI = ");
      Serial.print(LoRa.packetRssi());
      Serial.print(" dBm | SNR = ");
      Serial.print(LoRa.snr());
      Serial.println(" dB");
      
      // Vérification d'éventuelles erreurs
      uint8_t status = LoRa.status();
      if (status == SX126X_STATUS_CRC_ERR) {
        Serial.println("CRC error");
      } else if (status == SX126X_STATUS_HEADER_ERR) {
        Serial.println("Packet header error");
      }
    }
  }
  
  delay(1000);  // Délai avant la prochaine tentative de réception
}
*/

/*
#define NSS 3
#define NRESET 2
#define DIO1 0
#define BUSY 1
#define TX_POWER 13
#define SCK 8
#define MISO 9
#define MOSI 10

SX126x LoRa = new Module(NSS, DIO1, NRESET, BUSY);
//SX1262 LoRa = new Module(NSS,NRESET, BUSY);

void setup()
{

    Serial.begin(115200);
    while (!Serial);

    Serial.println("Initialisation du SPI...");
    SPI.begin(SCK, MISO, MOSI,NSS);
    // SPI.begin();  // SCK, MISO, MOSI, et SS
    delay(100);

    Serial.println("Initialisation du module LoRa SX1262...");
    int state = LoRa.begin();
    if (state == RADIOLIB_ERR_NONE)
    {
        Serial.println("Module SX1262 initialisé avec succès!");
    }
    else
    {
        Serial.print("Échec de l'initialisation du module SX1262. Code_ok_erreur : ");
        Serial.println(state);
        // while (true);
    }
    // ota.begin();
    // server.begin();
}

void loop()
{
    // ota.loop();

    Serial.println("Envoi du message : Hello, LoRa!");
    int state = LoRa.transmit("Hello, LoRa!");
    if (state == RADIOLIB_ERR_NONE)
    {
        Serial.println("Message envoyé avec succès!");
    }
    else
    {
        Serial.print("Échec de l'envoi du message. Code erreur: ");
        Serial.println(state);
    }
    delay(2000);

    Serial.println("Passage en mode réception...");
    String message;
    state = LoRa.receive(message);
    if (state == RADIOLIB_ERR_NONE)
    {
        Serial.print("Message reçu : ");
        Serial.println(message);
    }
    else
    {
        Serial.println("Aucun message reçu.");
    }
    delay(5000);
}
*/
/*
#include <Arduino.h>
#include <SPI.h>
#include <BaseLoRa.h>
#include <SX126x.h>

SX126x LoRa;

// Message à transmettre
char message[] = "HeLoRa World!";
uint8_t nBytes = sizeof(message);
uint8_t counter = 0;

void setup() {
  // Démarrage de la communication série
  Serial.begin(38400);
  
  Serial.println("Begin LoRa radio");
  // Initialisation du module LoRa avec les broches définies
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)) {
    Serial.println("Something wrong, can't begin LoRa radio");
    while (1);
  }
  
  // Configuration de la fréquence à 915 MHz (à adapter selon la réglementation locale)
  Serial.println("Set frequency to 915 MHz");
  LoRa.setFrequency(915000000);
  
  // Configuration de la puissance TX à +17 dBm
  Serial.println("Set TX power to +17 dBm");
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);
  
  // Configuration des paramètres de modulation
  Serial.println("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5");
  uint8_t sf = 7;           // Facteur d'étalement
  uint32_t bw = 125000;     // Bande passante de 125 kHz
  uint8_t cr = 5;           // Coding rate 4/5
  LoRa.setLoRaModulation(sf, bw, cr);
  
  // Configuration des paramètres de paquet
  Serial.println("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on");
  uint8_t headerType = SX126X_HEADER_EXPLICIT;  // Mode explicit
  uint16_t preambleLength = 12;                 // Longueur du préambule
  uint8_t payloadLength = 15;                   // Longueur du payload (message + compteur)
  bool crcType = true;                          // Activation du CRC
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);
  
  // Configuration du mot de synchronisation (sync word)
  Serial.println("Set synchronize word to 0x3444");
  LoRa.setSyncWord(0x3444);
  
  Serial.println("\n-- LORA TRANSMITTER / RECEIVER --\n");
}

void loop() {
  // ---- MODE TRANSMISSION ----
  // Préparation et envoi du paquet LoRa (message + compteur)
  LoRa.beginPacket();
  LoRa.write(message, nBytes);
  LoRa.write(counter);
  LoRa.endPacket();
  
  // Affichage du message transmis et incrémentation du compteur
  Serial.println();
  Serial.println();
  Serial.print("Transmitting: ");
  Serial.print(message);
  Serial.print("  ");
  Serial.println(counter++);
  
  // Attendre la fin de la transmission et afficher le temps d'émission
  LoRa.wait();
  Serial.print("Transmit time: ");
  Serial.print(LoRa.transmitTime());
  Serial.println(" ms");
  
  // ---- MODE RÉCEPTION ----
  // Demande de réception d'un nouveau paquet LoRa
  LoRa.request();
  // Attendre l'arrivée du paquet
  LoRa.wait();
  
  // Conversion des octets reçus en String
  if (LoRa.available() > 0) {
    String receivedMessage = "";
    
    // Lire tous les octets sauf le dernier (celui-ci contient le compteur)
    while (LoRa.available() > 1) {
      receivedMessage += (char)LoRa.read();
    }
    
    // Lecture du dernier octet (compteur)
    uint8_t receivedCounter = LoRa.read();
    
    // Affichage du message reçu et du compteur
    Serial.print("Received: ");
    Serial.print(receivedMessage);
    Serial.print("  ");
    Serial.println(receivedCounter);
    
    // Affichage des informations de signal (RSSI et SNR)
    Serial.print("Packet status: RSSI = ");
    Serial.print(LoRa.packetRssi());
    Serial.print(" dBm | SNR = ");
    Serial.print(LoRa.snr());
    Serial.println(" dB");
    
    // Vérification d'éventuelles erreurs (CRC ou header)
    uint8_t status = LoRa.status();
    if (status == SX126X_STATUS_CRC_ERR) {
      Serial.println("CRC error");
    } else if (status == SX126X_STATUS_HEADER_ERR) {
      Serial.println("Packet header error");
    }
  }
  
  // Délai avant la prochaine itération (ajustez si nécessaire)
  delay(500);
}

*/