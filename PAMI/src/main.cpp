#include <Arduino.h>
#include "OTA.h"

AsyncWebServer server(80);
CustomOTA ota("DVB_CDR", "davincibot", &server);

void setup() {
    Serial.begin(115200);
    ota.begin();
    server.begin();
}

void loop() {
    ota.loop();
}