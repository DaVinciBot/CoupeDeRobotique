#include <Arduino.h>
#include "motors.h"
#include "navigation.h"

#define LEFT_STEP_PIN 2
#define LEFT_DIR_PIN  3
#define LEFT_EN_PIN   4

#define RIGHT_STEP_PIN 5
#define RIGHT_DIR_PIN  6
#define RIGHT_EN_PIN   7


Motor leftMotor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, 200);
Motor rightMotor(RIGHT_STEP_PIN, RIGHT_DIR_PIN, RIGHT_EN_PIN, 200);

Navigation nav(&leftMotor, &rightMotor, 65, 150);

void setup() {
    Serial.begin(115200);

    leftMotor.init();
    rightMotor.init();

    leftMotor.enableMotor(true);
    leftMotor.setTargetSpeed(300);
    leftMotor.setAcceleration(100);

    rightMotor.enableMotor(true);
    rightMotor.setTargetSpeed(300);
    rightMotor.setAcceleration(100);

    Serial.println("Fin init");
}

void loop() {
    if(!nav.isBusy()) {
        static int state = 0;
        switch(state) {
            case 0:
                Serial.println("Avance de 200 mm");
                nav.forward(200);
                state = 1;
                break;
            case 1:
                Serial.println("Tourne 90 deg à gauche");
                nav.turn(90);
                state = 2;
                break;
            case 2:
                Serial.println("Avance de 100 mm");
                nav.forward(100);
                state = 3;
                break;
            default:
                break;
        }
    }

    nav.update();
}