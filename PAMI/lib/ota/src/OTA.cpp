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
        Serial.printf("OTA Progress Current: %d bytes, Final: %d bytes\n",
                      current, final);
    }
}

void onOTAEnd(bool success) {
    // Log when OTA has finished
    if (success) {
        Serial.println("OTA update finished successfully!");
    } else {
        Serial.println("[ERROR] There was an error during OTA update!");
    }
    // <Add your own code here>
}

void CustomOTA::begin() {
    if (!connectToStation()) {
        startFallbackAccessPoint();
    }

    startMdns();

    this->server->on("/", HTTP_GET, [](AsyncWebServerRequest* request) {
        request->redirect("/update");
    });

    ElegantOTA.begin(this->server);  // Start ElegantOTA

    // ElegantOTA callbacks
    ElegantOTA.onStart(onOTAStart);
    ElegantOTA.onProgress(onOTAProgress);
    ElegantOTA.onEnd(onOTAEnd);

    this->server->begin();
    Serial.println("OTA server started");
    Serial.printf("OTA URL: http://%s.local/update\n", this->hostname);
    Serial.println("Fallback AP URL: http://192.168.4.1/update");
}

CustomOTA::CustomOTA(const char* ssid,
                     const char* password,
                     const char* hostname,
                     const char* fallbackApSsid,
                     const char* fallbackApPassword,
                     AsyncWebServer* server) {
    this->ssid = ssid;
    this->password = password;
    this->hostname = hostname;
    this->fallbackApSsid = fallbackApSsid;
    this->fallbackApPassword = fallbackApPassword;
    this->server = server;
}

void CustomOTA::loop() {
    ElegantOTA.loop();
}

bool CustomOTA::connectToStation() {
    WiFi.mode(WIFI_STA);
    WiFi.setHostname(this->hostname);
    WiFi.begin(this->ssid, this->password);

    Serial.println("Connecting to WiFi...");
    Serial.printf("SSID: %s\n", this->ssid);

    while (WiFi.status() != WL_CONNECTED && _nb_try_wifi < 40) {
        delay(500);
        Serial.print(".");
        _nb_try_wifi++;
    }

    Serial.println();
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[OTA] WiFi connection failed");
        return false;
    }

    Serial.println("Connected to WiFi!");
    Serial.printf("IP address: %s\n", WiFi.localIP().toString().c_str());
    return true;
}

void CustomOTA::startFallbackAccessPoint() {
    IPAddress localIp(192, 168, 4, 1);
    IPAddress gateway(192, 168, 4, 1);
    IPAddress subnet(255, 255, 255, 0);

    WiFi.mode(WIFI_AP);
    WiFi.softAPConfig(localIp, gateway, subnet);
    WiFi.softAP(this->fallbackApSsid, this->fallbackApPassword);

    Serial.printf("[OTA] Started fallback AP: %s\n", this->fallbackApSsid);
    Serial.printf("[OTA] AP IP address: %s\n",
                  WiFi.softAPIP().toString().c_str());
}

void CustomOTA::startMdns() {
    if (MDNS.begin(this->hostname)) {
        MDNS.addService("http", "tcp", 80);
        Serial.printf("mDNS started: http://%s.local/update\n", this->hostname);
    } else {
        Serial.println("[OTA] mDNS start failed");
    }
}
