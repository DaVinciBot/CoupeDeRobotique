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

/*
#include <Arduino.h>
#include <SPI.h>
#include <BaseLoRa.h>
#include <SX126x.h>

SX126x LoRa;

// Message to transmit
char message[] = "HeLoRa World!";
uint8_t nBytes = sizeof(message);
uint8_t counter = 0;

void setup() {
  // Begin serial communication
  Serial.begin(38400);

  // Begin LoRa radio and set NSS, reset, busy, txen, and rxen pin with connected Arduino pins
  Serial.println("Begin LoRa radio");
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)) {
    Serial.println("Something wrong, can't begin LoRa radio");
    while (1);
  }

  // Set frequency to 915 MHz (check if this matches your region's frequency range)
  Serial.println("Set frequency to 915 MHz");
  LoRa.setFrequency(915000000);

  // Set TX power to +17 dBm (adjust if needed)
  Serial.println("Set TX power to +17 dBm");
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);

  // Configure modulation parameters (make sure both sender and receiver use same parameters)
  Serial.println("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5");
  uint8_t sf = 7;                                                     // LoRa spreading factor: 7
  uint32_t bw = 125000;                                               // Bandwidth: 125 kHz
  uint8_t cr = 5;                                                     // Coding rate: 4/5
  LoRa.setLoRaModulation(sf, bw, cr);

  // Configure packet parameters (ensure these match between sender and receiver)
  Serial.println("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on");
  uint8_t headerType = SX126X_HEADER_EXPLICIT;                        // Explicit header mode
  uint16_t preambleLength = 12;                                       // Set preamble length to 12
  uint8_t payloadLength = 15;                                         // Initialize payloadLength to 15
  bool crcType = true;                                                // Set CRC enable
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);

  // Set synchronize word for public network (0x3444)
  Serial.println("Set synchronize word to 0x3444");
  LoRa.setSyncWord(0x3444);

  Serial.println("\n-- LORA TRANSMITTER / RECEIVER --\n");
}

void loop() {
  
  // ---- TRANSMIT MODE ----
  // Transmit message and counter

  LoRa.beginPacket();
  LoRa.write(message, nBytes);
  LoRa.write(counter);
  LoRa.endPacket();

  // Print message and counter in serial
  Serial.println();
  Serial.println();
  Serial.print("Transmitting: ");
  Serial.print(message);
  Serial.print("  ");
  Serial.println(counter++);

  // Wait for transmission to finish
  LoRa.wait();

  // Print transmit time
  Serial.print("Transmit time: ");
  Serial.print(LoRa.transmitTime());
  Serial.println(" ms");
  */
  /*
  // ---- RECEIVE MODE ----
  // Request for receiving new LoRa packet
  LoRa.request();
  // Wait for incoming LoRa packet
  LoRa.wait();
  
  // Read received message and counter
  const uint8_t msgLen = LoRa.available() - 1;  // Subtract 1 for the counter byte
  if (msgLen > 0) {  // Ensure there is data to receive
    char receivedMessage[msgLen + 1];  // Extra byte for null terminator
    uint8_t receivedCounter;

    // Read message
    uint8_t i = 0;
    while (LoRa.available() > 1) {  // Read all message bytes except the last counter byte
      receivedMessage[i++] = LoRa.read();
    }

    // Null-terminate the string
    receivedMessage[i] = '\0';

    // Read the counter byte
    receivedCounter = LoRa.read();

    // Print received message and counter
    Serial.print("Received: ");
    Serial.print(receivedMessage);
    Serial.print("  ");
    Serial.println(receivedCounter);
  
    // Print packet/signal status including RSSI and SNR
    Serial.print("Packet status: RSSI = ");
    Serial.print(LoRa.packetRssi());
    Serial.print(" dBm | SNR = ");
    Serial.print(LoRa.snr());
    Serial.println(" dB");

    // Show received status in case of CRC or header error
    uint8_t status = LoRa.status();
    if (status == SX126X_STATUS_CRC_ERR) {
      Serial.println("CRC error");
    } else if (status == SX126X_STATUS_HEADER_ERR) {
      Serial.println("Packet header error");
    }
    
  }
  */
 /*
  // ---- RECEIVE MODE ----
  // Demande de réception d'un nouveau paquet LoRa
  LoRa.request();
  // Attente de l'arrivée du paquet
  LoRa.wait();

  // Vérifier s'il y a des données disponibles
  if (LoRa.available() > 0) {
      // Initialiser une String pour stocker le message reçu
    String receivedMessage = "";
    
    // Lire tous les octets sauf le dernier (on suppose que le dernier octet correspond au compteur)
    while (LoRa.available() > 1) {
      receivedMessage += (char)LoRa.read();
    }
  
    // Lire le dernier octet (compteur)
    uint8_t receivedCounter = LoRa.read();
  
    // Afficher le message reçu et le compteur
    Serial.print("Received: ");
    Serial.print(receivedMessage);
    Serial.print("  ");
    Serial.println(receivedCounter);
  
    // Afficher les informations de signal (RSSI et SNR)
    Serial.print("Packet status: RSSI = ");
    Serial.print(LoRa.packetRssi());
    Serial.print(" dBm | SNR = ");
    Serial.print(LoRa.snr());
    Serial.println(" dB");
  
    // Vérifier les erreurs éventuelles (CRC ou en-tête)
    uint8_t status = LoRa.status();
    if (status == SX126X_STATUS_CRC_ERR) {
      Serial.println("CRC error");
    } else if (status == SX126X_STATUS_HEADER_ERR) {
      Serial.println("Packet header error");
    }
  }

  // Delay before next transmission to avoid overloading the radio
  delay(100);
}
*/

// ok ?
/*
#include <SX126x.h>

SX126x LoRa;

// Message to transmit
char message[] = "HeLoRa World!";
uint8_t nBytes = sizeof(message);
uint8_t counter = 0;

void setup() {

  // Begin serial communication
  Serial.begin(38400);

  // Begin LoRa radio and set NSS, reset, busy, txen, and rxen pin with connected Arduino pins
  Serial.println("Begin LoRa radio");
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)){
    Serial.println("Something wrong, can't begin LoRa radio");
    while(1);
  }

  // Set frequency to 915 MHz
  Serial.println("Set frequency to 915 MHz");
  LoRa.setFrequency(915000000);

  // Set TX power
  Serial.println("Set TX power to +17 dBm");
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);

  // Configure modulation parameters
  Serial.println("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5");
  uint8_t sf = 7;                                                     // LoRa spreading factor: 7
  uint32_t bw = 125000;                                               // Bandwidth: 125 kHz
  uint8_t cr = 5;                                                     // Coding rate: 4/5
  LoRa.setLoRaModulation(sf, bw, cr);

  // Configure packet parameters
  Serial.println("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on");
  uint8_t headerType = SX126X_HEADER_EXPLICIT;                        // Explicit header mode
  uint16_t preambleLength = 12;                                       // Set preamble length to 12
  uint8_t payloadLength = 15;                                         // Initialize payloadLength to 15
  bool crcType = true;                                                // Set CRC enable
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);

  // Set synchronize word for public network (0x3444)
  Serial.println("Set synchronize word to 0x3444");
  LoRa.setSyncWord(0x3444);

  Serial.println("\n-- LORA TRANSMITTER / RECEIVER --\n");
}

void loop() {
  
  // ---- TRANSMIT MODE ----
  // Transmit message and counter
  LoRa.beginPacket();
  LoRa.write(message, nBytes);
  LoRa.write(counter);
  LoRa.endPacket();

  // Print message and counter in serial
  Serial.print("Transmitting: ");
  Serial.print(message);
  Serial.print("  ");
  Serial.println(counter++);
  
  // Wait for transmission to finish
  LoRa.wait();
  
  // Print transmit time
  Serial.print("Transmit time: ");
  Serial.print(LoRa.transmitTime());
  Serial.println(" ms");
  Serial.println();
  
  // ---- RECEIVE MODE ----
  // Request for receiving new LoRa packet
  LoRa.request();
  // Wait for incoming LoRa packet
  LoRa.wait();

  // Read received message and counter
  const uint8_t msgLen = LoRa.available() - 1;
  char receivedMessage[msgLen];
  uint8_t receivedCounter;
  
  uint8_t i = 0;
  while (LoRa.available() > 1) {
    receivedMessage[i++] = LoRa.read();
  }
  receivedCounter = LoRa.read();
  
  // Print received message and counter
  Serial.print("Received: ");
  Serial.print(receivedMessage);
  Serial.print("  ");
  Serial.println(receivedCounter);

  // Print packet/signal status including RSSI and SNR
  Serial.print("Packet status: RSSI = ");
  Serial.print(LoRa.packetRssi());
  Serial.print(" dBm | SNR = ");
  Serial.print(LoRa.snr());
  Serial.println(" dB");

  // Show received status in case of CRC or header error
  uint8_t status = LoRa.status();
  if (status == SX126X_STATUS_CRC_ERR) {
    Serial.println("CRC error");
  } else if (status == SX126X_STATUS_HEADER_ERR) {
    Serial.println("Packet header error");
  }
  
  // Delay before next transmission to avoid overloading the radio
  delay(5000);
}
*/

/*
// MOI
#include <SX126x.h>

SX126x LoRa;

void setup() {

  // Begin serial communication
  Serial.begin(38400);

  // Begin LoRa radio and set NSS, reset, busy, txen, and rxen pin with connected arduino pins
  Serial.println("Begin LoRa radio");
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = 2, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)){
    Serial.println("Something wrong, can't begin LoRa radio");
    while(1);
  }

  // Configure TCXO or XTAL used in RF module
  Serial.println("Set RF module to use TCXO as clock reference");
  uint8_t dio3Voltage = SX126X_DIO3_OUTPUT_1_8;
  uint32_t tcxoDelay = SX126X_TCXO_DELAY_10;
  LoRa.setDio3TcxoCtrl(dio3Voltage, tcxoDelay);
  
  // Set frequency to 915 Mhz
  Serial.println("Set frequency to 915 Mhz");
  LoRa.setFrequency(915000000);

  // Set RX gain to boosted gain
  Serial.println("Set RX gain to boosted gain");
  LoRa.setRxGain(SX126X_RX_GAIN_BOOSTED);

  // Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
  Serial.println("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5");
  uint8_t sf = 7;
  uint32_t bw = 125000;
  uint8_t cr = 5;
  LoRa.setLoRaModulation(sf, bw, cr);

  // Configure packet parameter including header type, preamble length, payload length, and CRC type
  Serial.println("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on");
  uint8_t headerType = SX126X_HEADER_EXPLICIT;
  uint16_t preambleLength = 12;
  uint8_t payloadLength = 15;
  bool crcType = true;
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);

  // Set syncronize word for public network (0x3444)
  Serial.println("Set syncronize word to 0x3444");
  LoRa.setSyncWord(0x3444);

  Serial.println("\n-- LORA RECEIVER LISTEN --\n");
  
}

void loop() {

  // Listen for a LoRa packet in 10 ms and sleep in 10 ms
  uint32_t rxPeriod = 10;
  uint32_t sleepPeriod = 10;
  LoRa.listen(rxPeriod, sleepPeriod);

  // Check for incoming LoRa packet
  const uint8_t msgLen = LoRa.available();
  if (msgLen) {

    // Put received packet to message and counter variable
    const uint8_t msgLen = LoRa.available() - 1;
    char message[msgLen];
    uint8_t counter;
    uint8_t i=0;
    while (LoRa.available() > 1){
      message[i++] = LoRa.read();
    }
    counter = LoRa.read();

    // Print received message and counter in serial
    Serial.print(message);
    Serial.print("  ");
    Serial.println(counter);

    // Print packet/signal status including package RSSI and SNR
    Serial.print("Packet status: RSSI = ");
    Serial.print(LoRa.packetRssi());
    Serial.print(" dBm | SNR = ");
    Serial.print(LoRa.snr());
    Serial.println(" dB");

    // Show received status in case CRC or header error occur
    uint8_t status = LoRa.status();
    if (status == SX126X_STATUS_RX_TIMEOUT) Serial.println("Receive timeout");
    else if (status == SX126X_STATUS_CRC_ERR) Serial.println("CRC error");
    else if (status == SX126X_STATUS_HEADER_ERR) Serial.println("Packet header error");
    Serial.println();

  }

}
*/
/*
// listen
#include <SX126x.h>

SX126x LoRa;

void setup() {

  // Begin serial communication
  Serial.begin(38400);

  // Begin LoRa radio and set NSS, reset, busy, txen, and rxen pin with connected arduino pins
  Serial.println("Begin LoRa radio");
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = 2, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)){
    Serial.println("Something wrong, can't begin LoRa radio");
    while(1);
  }

  // Configure TCXO or XTAL used in RF module
  Serial.println("Set RF module to use TCXO as clock reference");
  uint8_t dio3Voltage = SX126X_DIO3_OUTPUT_1_8;
  uint32_t tcxoDelay = SX126X_TCXO_DELAY_10;
  LoRa.setDio3TcxoCtrl(dio3Voltage, tcxoDelay);
  
  // Set frequency to 915 Mhz
  Serial.println("Set frequency to 915 Mhz");
  LoRa.setFrequency(915000000);

  // Set RX gain to boosted gain
  Serial.println("Set RX gain to boosted gain");
  LoRa.setRxGain(SX126X_RX_GAIN_BOOSTED);

  // Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
  Serial.println("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5");
  uint8_t sf = 7;
  uint32_t bw = 125000;
  uint8_t cr = 5;
  LoRa.setLoRaModulation(sf, bw, cr);

  // Configure packet parameter including header type, preamble length, payload length, and CRC type
  Serial.println("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on");
  uint8_t headerType = SX126X_HEADER_EXPLICIT;
  uint16_t preambleLength = 12;
  uint8_t payloadLength = 15;
  bool crcType = true;
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);

  // Set syncronize word for public network (0x3444)
  Serial.println("Set syncronize word to 0x3444");
  LoRa.setSyncWord(0x3444);

  Serial.println("\n-- LORA RECEIVER LISTEN --\n");
  
}

void loop() {

  // Listen for a LoRa packet in 10 ms and sleep in 10 ms
  uint32_t rxPeriod = 10;
  uint32_t sleepPeriod = 10;
  LoRa.listen(rxPeriod, sleepPeriod);

  // Check for incoming LoRa packet
  const uint8_t msgLen = LoRa.available();
  if (msgLen) {

    // Put received packet to message and counter variable
    const uint8_t msgLen = LoRa.available() - 1;
    char message[msgLen];
    uint8_t counter;
    uint8_t i=0;
    while (LoRa.available() > 1){
      message[i++] = LoRa.read();
    }
    counter = LoRa.read();

    // Print received message and counter in serial
    Serial.print(message);
    Serial.print("  ");
    Serial.println(counter);

    // Print packet/signal status including package RSSI and SNR
    Serial.print("Packet status: RSSI = ");
    Serial.print(LoRa.packetRssi());
    Serial.print(" dBm | SNR = ");
    Serial.print(LoRa.snr());
    Serial.println(" dB");

    // Show received status in case CRC or header error occur
    uint8_t status = LoRa.status();
    if (status == SX126X_STATUS_RX_TIMEOUT) Serial.println("Receive timeout");
    else if (status == SX126X_STATUS_CRC_ERR) Serial.println("CRC error");
    else if (status == SX126X_STATUS_HEADER_ERR) Serial.println("Packet header error");
    Serial.println();

  }

}
*/
/*
//first receivv
#include <SX126x.h>

SX126x LoRa;

void setup() {

  // Begin serial communication
  Serial.begin(38400);

  // Uncomment below to use non default SPI port
  //SPIClass SPI_2(PB15, PB14, PB13);
  //LoRa.setSPI(SPI_2, 16000000);

  // Begin LoRa radio and set NSS, reset, busy, txen, and rxen pin with connected arduino pins
  // IRQ pin not used in this example (set to -1). Set txen and rxen pin to -1 if RF module doesn't have one
  Serial.println("Begin LoRa radio");
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)){
    Serial.println("Something wrong, can't begin LoRa radio");
    while(1);
  }

  // Optionally configure TCXO or XTAL used in RF module
  // Different RF module can have different clock, so make sure clock source is configured correctly
  // uncomment code below to use TCXO
  Serial.println("Set RF module to use TCXO as clock reference");
  uint8_t dio3Voltage = SX126X_DIO3_OUTPUT_1_8;
  uint32_t tcxoDelay = SX126X_TCXO_DELAY_10;
  LoRa.setDio3TcxoCtrl(dio3Voltage, tcxoDelay);
  // uncomment code below to use XTAL
  //uint8_t xtalA = 0x12;
  //uint8_t xtalB = 0x12;
  //Serial.println("Set RF module to use XTAL as clock reference");
  //LoRa.setXtalCap(xtalA, xtalB);

  // Optionally configure DIO2 as RF switch control
  // This is usually used for a LoRa module without TXEN and RXEN pins
  //LoRa.setDio2RfSwitch(true);

  // Set frequency to 915 Mhz
  Serial.println("Set frequency to 915 Mhz");
  LoRa.setFrequency(915000000);

  // Set RX gain. RX gain option are power saving gain or boosted gain
  Serial.println("Set RX gain to power saving gain");
  LoRa.setRxGain(SX126X_RX_GAIN_POWER_SAVING);                        // Power saving gain

  // Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
  // Transmitter must have same SF and BW setting so receiver can receive LoRa packet
  Serial.println("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5");
  uint8_t sf = 7;                                                     // LoRa spreading factor: 7
  uint32_t bw = 125000;                                               // Bandwidth: 125 kHz
  uint8_t cr = 5;                                                     // Coding rate: 4/5
  LoRa.setLoRaModulation(sf, bw, cr);

  // Configure packet parameter including header type, preamble length, payload length, and CRC type
  // The explicit packet includes header contain CR, number of byte, and CRC type
  // Packet with explicit header can't be received by receiver with implicit header mode
  Serial.println("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on");
  uint8_t headerType = SX126X_HEADER_EXPLICIT;                        // Explicit header mode
  uint16_t preambleLength = 12;                                       // Set preamble length to 12
  uint8_t payloadLength = 15;                                         // Initialize payloadLength to 15
  bool crcType = true;                                                // Set CRC enable
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);

  // Set syncronize word for public network (0x3444)
  Serial.println("Set syncronize word to 0x3444");
  LoRa.setSyncWord(0x3444);

  Serial.println("\n-- LORA RECEIVER --\n");
  
}

void loop() {
  
  // Request for receiving new LoRa packet
  LoRa.request();
  // Wait for incoming LoRa packet
  LoRa.wait();

  // Put received packet to message and counter variable
  // read() and available() method must be called after request() or listen() method
  const uint8_t msgLen = LoRa.available() - 1;
  char message[msgLen];
  uint8_t counter;
  // available() method return remaining received payload length and will decrement each read() or get() method called
  uint8_t i=0;
  while (LoRa.available() > 1){
    message[i++] = LoRa.read();
  }
  counter = LoRa.read();
  
  // Print received message and counter in serial
  Serial.print(message);
  Serial.print("  ");
  Serial.println(counter);

  // Print packet/signal status including package RSSI and SNR
  Serial.print("Packet status: RSSI = ");
  Serial.print(LoRa.packetRssi());
  Serial.print(" dBm | SNR = ");
  Serial.print(LoRa.snr());
  Serial.println(" dB");
  
  // Show received status in case CRC or header error occur
  uint8_t status = LoRa.status();
  if (status == SX126X_STATUS_CRC_ERR) Serial.println("CRC error");
  else if (status == SX126X_STATUS_HEADER_ERR) Serial.println("Packet header error");
  Serial.println();

}
*/
/*
SX126x LoRa;

// Message to transmit
char message[] = "HeLoRa World!";
uint8_t nBytes = sizeof(message);
uint8_t counter = 0;

void setup() {

  // Begin serial communication
  Serial.begin(38400);

  // Uncomment below to use non default SPI port
  //SPIClass SPI_2(PB15, PB14, PB13);
  //LoRa.setSPI(SPI_2, 16000000);

  // Begin LoRa radio and set NSS, reset, busy, IRQ, txen, and rxen pin with connected arduino pins
  // IRQ pin not used in this example (set to -1). Set txen and rxen pin to -1 if RF module doesn't have one
  Serial.println("Begin LoRa radio");
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)){
    Serial.println("Something wrong, can't begin LoRa radio");
    while(1);
  }

  // Optionally configure TCXO or XTAL used in RF module
  // Different RF module can have different clock, so make sure clock source is configured correctly
  // uncomment code below to use TCXO
  Serial.println("Set RF module to use TCXO as clock reference");
  uint8_t dio3Voltage = SX126X_DIO3_OUTPUT_1_8;
  uint32_t tcxoDelay = SX126X_TCXO_DELAY_10;
  LoRa.setDio3TcxoCtrl(dio3Voltage, tcxoDelay);
  // uncomment code below to use XTAL
  //uint8_t xtalA = 0x12;
  //uint8_t xtalB = 0x12;
  //Serial.println("Set RF module to use XTAL as clock reference");
  //LoRa.setXtalCap(xtalA, xtalB);

  // Optionally configure DIO2 as RF switch control
  // This is usually used for a LoRa module without TXEN and RXEN pins
  //LoRa.setDio2RfSwitch(true);

  // Set frequency to 915 Mhz
  Serial.println("Set frequency to 915 Mhz");
  LoRa.setFrequency(915000000);

  // Set TX power, default power for SX1262 and SX1268 are +22 dBm and for SX1261 is +14 dBm
  // This function will set PA config with optimal setting for requested TX power
  Serial.println("Set TX power to +17 dBm");
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);                        // TX power +17 dBm for SX1262

  // Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
  // Receiver must have same SF and BW setting with transmitter to be able to receive LoRa packet
  Serial.println("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5");
  uint8_t sf = 7;                                                     // LoRa spreading factor: 7
  uint32_t bw = 125000;                                               // Bandwidth: 125 kHz
  uint8_t cr = 5;                                                     // Coding rate: 4/5
  LoRa.setLoRaModulation(sf, bw, cr);

  // Configure packet parameter including header type, preamble length, payload length, and CRC type
  // The explicit packet includes header contain CR, number of byte, and CRC type
  // Receiver can receive packet with different CR and packet parameters in explicit header mode
  Serial.println("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on");
  uint8_t headerType = SX126X_HEADER_EXPLICIT;                        // Explicit header mode
  uint16_t preambleLength = 12;                                       // Set preamble length to 12
  uint8_t payloadLength = 15;                                         // Initialize payloadLength to 15
  bool crcType = true;                                                // Set CRC enable
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);

  // Set syncronize word for public network (0x3444)
  Serial.println("Set syncronize word to 0x3444");
  LoRa.setSyncWord(0x3444);

  Serial.println("\n-- LORA TRANSMITTER --\n");
  
}

void loop() {
  
  // Transmit message and counter
  // write() method must be placed between beginPacket() and endPacket()
  LoRa.beginPacket();
  LoRa.write(message, nBytes);
  LoRa.write(counter);
  LoRa.endPacket();

  // Print message and counter in serial
  Serial.print(message);
  Serial.print("  ");
  Serial.println(counter++);

  // Wait until modulation process for transmitting packet finish
  LoRa.wait();

  // Print transmit time
  Serial.print("Transmit time: ");
  Serial.print(LoRa.transmitTime());
  Serial.println(" ms");
  Serial.println();

  // Don't load RF module with continous transmit
  delay(5000);

}
*/
/*
void setup() {
    Serial.begin(115200);
    Serial.println("ca marche pas");
    delay(1000); // Petit délai pour la connexion série

    SPI.begin(8, 9, 10); // SCK = 5, MISO = 6, MOSI = 7
    pinMode(3, OUTPUT); // NSS
    digitalWrite(3, HIGH);

    Serial.println("Testing SPI...");
    digitalWrite(3, LOW);
    uint8_t response = SPI.transfer(0x42); // Lire registre version
    digitalWrite(3, HIGH);

    Serial.print("SPI response: ");
    Serial.println(response, HEX);

    if (response == 0x22 || response == 0x12) {
        Serial.println("SX1262 détecté !");
    } else {
        Serial.println("SX1262 non détecté ! Vérifiez le câblage.");
    }
}

void loop() { }
*/


/*
SX1262 LoRa;
void setup() {
    LoRa.setSPI(SPI2, 16000000);
    LoRa.setPins(10, 9, 2, 4, 8, 7);
    LoRa.begin();
    LoRa.setTxPower(22, SX126X_TX_POWER_SX1262);
    LoRa.setRxGain(LORA_RX_GAIN_POWER_SAVING);
    LoRa.setFrequency(915000000);
    LoRa.setLoRaModulation(8, 125000, 5, false);
    // set explicit header mode, preamble length 12, payload length 15, CRC on and no invert IQ operation
    LoRa.setLoRaPacket(LORA_HEADER_EXPLICIT, 12, 15, true, false);
    // set explicit header mode, preamble length 12, payload length 15, CRC on and no invert IQ operation
    LoRa.setLoRaPacket(LORA_HEADER_EXPLICIT, 12, 15, true, false);
    // Set syncronize word for public network (0x3444)
    LoRa.setSyncWord(0x3444);
  }

  void loop() {
    // message and counter to transmit
    char message[] = "HeLoRa World!";
    uint8_t counter = 0;

    LoRa.beginPacket();
    LoRa.write(message, sizeof(message)); // write multiple bytes
    LoRa.write(counter++);                // write single byte
    LoRa.endPacket();
    LoRa.wait();

    LoRa.request();
    LoRa.wait();

    // get message and counter in last byte
    const uint8_t length = LoRa.available() - 1;
    char message[length];
    uint8_t i=0;
    while (LoRa.available() > 1){
        message[i++] = LoRa.read();         // read multiple bytes
    }
    uint8_t counter = LoRa.read();        // read single byte
  }
*/
