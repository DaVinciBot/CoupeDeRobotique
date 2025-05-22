#include <Arduino.h>
#include "motor.h"
#include "navigation.h"
#include "rolling_basis.h"


// #------- MOTOR CONFIGURATION -------#
#define LEFT_DIR_PIN 3
#define LEFT_STEP_PIN 46
#define LEFT_EN_PIN 9

#define RIGHT_DIR_PIN 21
#define RIGHT_STEP_PIN 47
#define RIGHT_EN_PIN 48

// #------- LORA CONFIGURATION -------#
#define SS 10 // NSS pin
#define RST 16 // RESET pin
#define BUSY 15 // BUSY pin

// ESP XIAO DEVKIT PINOUT
// #define SS 4 // NSS pin
// #define RST 3 // RESET pin
// #define BUSY 2 // BUSY pin

// #-------- DEV CONFIGURATION ---------#
#define ENABLE_OTA false

