#include "../include/OTA.h"

unsigned long ota_progress_millis = 0;


void onOTAStart() {
  // Log when OTA has started
  Serial.println("OTA update started!");
}

void onOTAProgress(size_t current, size_t final) {
  // Log every 1 second
  if (millis() - ota_progress_millis > 1000) {
    ota_progress_millis = millis();
    Serial.printf("OTA Progress Current: %u bytes, Final: %u bytes\n", current, final);
  }
}

void onOTAEnd(bool success) {
  // Log when OTA has finished
  if (success) {
    Serial.println("OTA update finished successfully!");
  } else {
    Serial.println("There was an error during OTA update!");
  }
  // <Add your own code here>
}

void CustomOTA::begin() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(this->ssid, this->password);
  Serial.println("");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    if (_nb_try_wifi > 120) {
      Serial.println("Failed to connect to WiFi, rebooting...");
      ESP.restart();
      break;
    }
    delay(500);
    Serial.print(".");
    _nb_try_wifi++;
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  this->server->on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->redirect("/update");
  });
  
  ElegantOTA.begin(this->server);      // Start ElegantOTA

  // ElegantOTA callbacks
  ElegantOTA.onStart(onOTAStart);
  ElegantOTA.onProgress(onOTAProgress);
  ElegantOTA.onEnd(onOTAEnd);
}

CustomOTA::CustomOTA(const char *ssid, const char *password, AsyncWebServer *server) {
  this->ssid = ssid;
  this->password = password;
  this->server = server;
}

void CustomOTA::loop() {
  ElegantOTA.loop();
}