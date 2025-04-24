// #include "com.h"
#include "config.h"

AsyncWebServer server(80);
CustomOTA ota("DVB", "davincibot", &server);
// Com *com = new Com(); // LoRa object
int counter = 0;

void print_debug(byte *msg, byte size)
{
    Serial.print("Received message: ");
    for (int i = 0; i < size; i++)
    {
        Serial.print(msg[i], HEX);
        Serial.print(" ");
    }
    Serial.println();
}

void (*callback_functions[256])(byte *msg, byte size);

void initialize_callback_functions()
{
    // callback_functions[SET_POSITION] = &set_speed_and_position;
    // callback_functions[SET_PID] = &set_pid;
    // callback_functions[SET_ODOMETRIE] = &set_odometrie;
    //   callback_functions[RESET_PAMI] = &reset_teensy;
    // callback_functions[PRINT] = &print_debug;
}
void setup()
{
    Serial.begin(115200);
    Serial.println("\n-- LORA TRANSMITTER / RECEIVER --\n");
    // com->begin(SS, RST, BUSY, IRQ, TXEN, RXEN); // NSS, RESET, BUSY, IRQ, TXEN, RXEN pins

    ota.begin();

    initialize_callback_functions();
}

void loop()
{
    // com->handle_callback(callback_functions);
    ota.loop(); // Handle OTA updates

    // if (counter++ > 4096)
    // {
    //     // com->print("test message"); // Send a test message
    //     counter = 0;
    // }

    // ---- RECEIVE MODE ----
    // Request for receiving new LoRa packet
    //   LoRa.request();
    //   // Wait for incoming LoRa packet
    //   LoRa.wait();

    //   // Read received message and counter
    //   const uint8_t msgLen = LoRa.available() - 1;
    //   char receivedMessage[msgLen];
    //   uint8_t receivedCounter;

    //   uint8_t i = 0;
    //   while (LoRa.available() > 1) {
    //     receivedMessage[i++] = LoRa.read();
    //   }
    //   receivedCounter = LoRa.read();

    //   // Print received message and counter
    //   Serial.print("Received: ");
    //   Serial.print(receivedMessage);
    //   Serial.print("  ");
    //   Serial.println(receivedCounter);

    //   // Print packet/signal status including RSSI and SNR
    //   Serial.print("Packet status: RSSI = ");
    //   Serial.print(LoRa.packetRssi());
    //   Serial.print(" dBm | SNR = ");
    //   Serial.print(LoRa.snr());
    //   Serial.println(" dB");

    //   // Show received status in case of CRC or header error
    //   uint8_t status = LoRa.status();
    //   if (status == SX126X_STATUS_CRC_ERR) {
    //     Serial.println("CRC error");
    //   } else if (status == SX126X_STATUS_HEADER_ERR) {
    //     Serial.println("Packet header error");
}
