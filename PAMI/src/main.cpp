#include <Arduino.h>
#include "OTA.h"
#include "motor.h"
#include "navigation.h"
#include "rolling_basis.h"

#define LEFT_STEP_PIN 2
#define LEFT_DIR_PIN 3
#define LEFT_EN_PIN 1

Motor leftMotor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, 400);

AsyncWebServer server(80);
CustomOTA ota("DVB_CDR", "davincibot", &server);

void setup()
{
    Serial.begin(115200);

    leftMotor.init();

    leftMotor.enableMotor(true);

    leftMotor.setAcceleration(100);

    leftMotor.setTargetSpeed(400);

    digitalWrite(LEFT_DIR_PIN, HIGH);

    ota.begin();
    server.begin();
}

void loop()
{

    for (int i = 0; i < 800; i++)
    {
        leftMotor.update();
    }

    ota.loop();
}