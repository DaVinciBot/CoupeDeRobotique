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
#define SS 8 // NSS pin
#define RST 9 // RESET pin
#define BUSY 8 // BUSY pin
#define IRQ 7 // IRQ pin
#define TXEN 6 // TXEN pin
#define RXEN 5 // RXEN pin

// #-------- DEV CONFIGURATION ---------#
#define ENABLE_OTA false

