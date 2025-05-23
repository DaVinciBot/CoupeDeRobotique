#include <Arduino.h>
#include "motor.h"
#include "navigation.h"
#include "rolling_basis.h"


// #------- MOTOR CONFIGURATION -------#
#define LEFT_STEP_PIN 16
#define LEFT_DIR_PIN 15
#define LEFT_EN_PIN 17
#define LEFT_STEPS_PER_REV 400

#define RIGHT_STEP_PIN 24
#define RIGHT_DIR_PIN 23
#define RIGHT_EN_PIN 25
#define RIGHT_STEPS_PER_REV 400

// FIXME: bonnes valeurs
#define WHEEL_DIAMETER_MM 70
#define WHEEL_BASE_MM 150

#define MAX_LINEAR_SPEED_MM_PER_S 100
#define MAX_ANGULAR_SPEED_RAD_PER_S 1.0

// #------- LORA CONFIGURATION -------#
#define SS 10 // NSS pin
#define RST 9 // RESET pin
#define BUSY 8 // BUSY pin
#define IRQ 7 // IRQ pin
#define TXEN 6 // TXEN pin
#define RXEN 5 // RXEN pin

// #-------- DEV CONFIGURATION ---------#
#define ENABLE_OTA false

