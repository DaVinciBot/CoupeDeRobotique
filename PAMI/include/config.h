#include <Arduino.h>
#include "motor.h"
#include "navigation.h"
#include "rolling_basis.h"


// #------- MOTOR CONFIGURATION -------#
#define LEFT_STEP_PIN 16
#define LEFT_DIR_PIN 15
#define LEFT_EN_PIN 17

#define RIGHT_STEP_PIN 24
#define RIGHT_DIR_PIN 23
#define RIGHT_EN_PIN 25

// #------- LORA CONFIGURATION -------#
#define SS 10 // NSS pin
#define RST 9 // RESET pin
#define BUSY 8 // BUSY pin
#define IRQ 7 // IRQ pin
#define TXEN 6 // TXEN pin
#define RXEN 5 // RXEN pin

// #-------- DEV CONFIGURATION ---------#
#define ENABLE_OTA false

