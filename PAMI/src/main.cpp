#include <Arduino.h>
#include "OTA.h"
#include "motors.h"
#include "navigation.h"

#define LEFT_STEP_PIN 3
#define LEFT_DIR_PIN  2
#define LEFT_EN_PIN   4


Motor leftMotor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, 200);

AsyncWebServer server(80);
CustomOTA ota("DVB_CDR", "davincibot", &server);

void setup()
{
    Serial.begin(115200);

    leftMotor.init();

    leftMotor.enableMotor(true);

    leftMotor.setAcceleration(100);

    Serial.println("Fin init");
    ota.begin();
    server.begin();
}

void loop() {
    
    leftMotor.setTargetSpeed(300);
    leftMotor.update();

    ota.loop();
}