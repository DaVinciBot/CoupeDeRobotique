#ifndef OTA_h
#define OTA_h

#if defined(ESP8266)
#include <ESP8266WiFi.h>
#elif defined(ESP32)
#include <WiFi.h>
#endif
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "ElegantOTA.h"

class CustomOTA {
   public:
    void begin();

    void addKnownNetwork(const char* ssid, const char* password);
    void loop();

    CustomOTA(const char* ssid, const char* password, AsyncWebServer* server);
    // CustomOTA(const char *ssid, const char *password);
    // CustomOTA();

   private:
    ElegantOTAClass ElegantOTA;
    const char* ssid;
    const char* password;
    AsyncWebServer* server;
    int _nb_try_wifi = 0;
};

void onOTAEnd(bool success);
void onOTAProgress(size_t current, size_t final);
void onOTAStart();
#endif
