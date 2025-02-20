#include <SPI.h>
#include <RadioLib.h>


#define LORA_NSS    7  // Chip Select (CS)
#define LORA_RST    8  // Reset
#define LORA_BUSY   2  // Busy
#define LORA_DIO1   1  // Interrupt
#define LORA_MOSI   6  // MOSI
#define LORA_MISO   5  // MISO
#define LORA_SCK    4  // SCK


SX1262 lora = new Module(LORA_NSS, LORA_DIO1, LORA_RST, LORA_BUSY);

void setup() {
    Serial.begin(115200);
    while (!Serial);

    Serial.println("Initializing LoRa Module...");

    // Initialize LoRa
    if (lora.begin(915.0, 125.0, 7, 5, 22, 8, 0) == RADIOLIB_ERR_NONE) {
        Serial.println("LoRa Module Initialized Successfully!");
    } else {
        Serial.println("LoRa Module Initialization Failed!");
        while (true);
    }
}

void loop() {
    Serial.println("Sending LoRa Packet...");
    int state = lora.transmit("Hello from Xiao ESP32-S3!");

    if (state == RADIOLIB_ERR_NONE) {
        Serial.println("Packet Sent Successfully!");
    } else {
        Serial.println("Failed to send packet!");
    }

    // Wait for a response (optional)
    Serial.println("Waiting for a packet...");
    String received;
    state = lora.receive(received);

    if (state == RADIOLIB_ERR_NONE) {
        Serial.print("Received packet: ");
        Serial.println(received);
    } else {
        Serial.println("No packet received...");
    }

    delay(5000); // Wait before sending the next packet
}
