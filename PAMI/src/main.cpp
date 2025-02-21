#include <SPI.h>
#include <RadioLib.h>

// Définition des broches pour XIAO ESP32S3
#define NSS 10
#define NRESET 9
#define DIO1 8
#define BUSY 7
#define TX_POWER 13 // Puissance d'émission en dBm

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
    envoyerMessage("Hello, LoRa!");
    recevoirMessage();
    delay(5000); // Envoi toutes les 5 secondes
}

void envoyerMessage(String message) {
    Serial.print("Envoi du message : ");
    Serial.println(message);
    if (LoRa.transmit(message) == RADIOLIB_ERR_NONE) {
        Serial.println("Message envoyé avec succès!");
    } else {
        Serial.println("Échec de l'envoi du message.");
    }
}

void recevoirMessage() {
    String message;
    int state = LoRa.receive(message);
    if (state == RADIOLIB_ERR_NONE) {
        Serial.print("Message reçu : ");
        Serial.println(message);
    }
}
