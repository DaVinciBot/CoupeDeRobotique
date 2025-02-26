#include <Arduino.h>
#include "motors.h"
#include "navigation.h"

#define LEFT_STEP_PIN 2
#define LEFT_DIR_PIN 3
#define LEFT_EN_PIN 4

#define RIGHT_STEP_PIN 5
#define RIGHT_DIR_PIN 6
#define RIGHT_EN_PIN 7

Motor leftMotor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, 200);
Motor rightMotor(RIGHT_STEP_PIN, RIGHT_DIR_PIN, RIGHT_EN_PIN, 200);

Navigation nav(&leftMotor, &rightMotor, 65.0f, 150.0f);

void setup()
{
    Serial.begin(115200);

    leftMotor.init();
    rightMotor.init();
    leftMotor.enableMotor(true);
    rightMotor.enableMotor(true);

    leftMotor.setAcceleration(100);
    rightMotor.setAcceleration(100);

    Serial.println("Démarrage du robot");
}

void loop()
{
    if (!nav.isBusy())
    {
        nav.setLinearAngularSpeed(50.0f, 45.0f);
    }

    nav.update();
}