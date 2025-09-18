#include "../include/OTA.h"
#include "spdlog/spdlog.h"

unsigned long ota_progress_millis = 0;

void onOTAStart() {
    // Log when OTA has started
    spdlog::info("OTA update started!");
}

void onOTAProgress(size_t current, size_t final) {
    // Log every 1 second
    if (millis() - ota_progress_millis > 1000) {
        ota_progress_millis = millis();
        spdlog::info("OTA Progress Current: {} bytes, Final: {} bytes",
                      current, final);
    }
}

void onOTAEnd(bool success) {
    // Log when OTA has finished
    if (success) {
        spdlog::info("OTA update finished successfully!");
    } else {
        spdlog::error("There was an error during OTA update!");
    }
    // <Add your own code here>
}

void CustomOTA::begin() {
    WiFi.mode(WIFI_STA);
    // Connect to WiFi
    WiFi.begin(this->ssid, this->password);
    if (Serial) {
        spdlog::info("Connecting to WiFi...");
        spdlog::info("Connecting to {} with password {}", this->ssid, this->password);
    }

    // Wait for connection
    while (WiFi.status() != WL_CONNECTED) {
        if (_nb_try_wifi > 120) {
            spdlog::error("Failed to connect to WiFi, rebooting...");
            ESP.restart();
            break;
        }
        delay(500);
        spdlog::info(".");
        _nb_try_wifi++;
    }
    if (Serial) {
        spdlog::info("Connected to WiFi!");
        spdlog::info("IP address: {}", WiFi.localIP());
    }

    this->server->on("/", HTTP_GET, [](AsyncWebServerRequest* request) {
        request->redirect("/update");
    });

    ElegantOTA.begin(this->server);  // Start ElegantOTA

    // ElegantOTA callbacks
    ElegantOTA.onStart(onOTAStart);
    ElegantOTA.onProgress(onOTAProgress);
    ElegantOTA.onEnd(onOTAEnd);
}

CustomOTA::CustomOTA(const char* ssid,
                     const char* password,
                     AsyncWebServer* server) {
    this->ssid = ssid;
    this->password = password;
    this->server = server;
}

void CustomOTA::loop() {
    ElegantOTA.loop();
}
