#include <Arduino.h>
#include "OTA.h"
#include "motor.h"
#include "navigation.h"
#include "rolling_basis.h"
#include "gs2_lidar.hpp"

#define LEFT_STEP_PIN 2
#define LEFT_DIR_PIN 3
#define LEFT_EN_PIN 1

#define RX_LIDAR 44
#define TX_LIDAR 43

Gs2Lidar lidar(Serial1, RX_LIDAR, TX_LIDAR,
               116,   // à modif
               130);  // à modif si necessaire


Motor leftMotor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, 400);

AsyncWebServer server(80);
CustomOTA ota("DVB_CDR", "davincibot", &server);

void setup()
{
    Serial.begin(115200);
    
    lidar.begin();

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
    lidar.task();

     if (lidar.obstacleDetected())
        Serial.println("Obstacle proche !");
    if (lidar.cliffDetected())
        Serial.println("Vide détecté !");

    ota.loop();
}
