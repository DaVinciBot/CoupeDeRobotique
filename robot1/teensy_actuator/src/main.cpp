#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>

#include <Adafruit_PWMServoDriver.h>
#include <LiquidCrystal_I2C.h>
#include <Bonezegei_A4988.h>

void setup() {
    for (int pin = 0; pin <= 7; pin++) {
        pinMode(pin, OUTPUT);
    }
}

void loop() {
    for (int pin = 0; pin <= 7; pin++) {
        digitalWrite(pin, HIGH);
        delay(200);
    }

    for (int pin = 0; pin <= 7; pin++) {
        digitalWrite(pin, LOW);
        delay(200);
    }
}