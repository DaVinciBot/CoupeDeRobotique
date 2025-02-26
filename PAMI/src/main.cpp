#include <Arduino.h>
#include "motors.h"
#include "navigation.h"

#define LEFT_STEP_PIN 1
#define LEFT_DIR_PIN 0
#define LEFT_EN_PIN 2

Motor leftMotor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, 200);


void setup()
{
    Serial.begin(115200);

    leftMotor.init();
    leftMotor.enableMotor(true);

    leftMotor.setAcceleration(100);

    Serial.println("Démarrage du robot");
}

void loop()
{
    leftMotor.setTargetSpeed(100);

    leftMotor.update();

    delay(100);
}