#include <Arduino.h>
#include "motor.h"
#include "navigation.h"
#include "rolling_basis.h"
#include "lidar_pami.h"


// #------- MOTOR CONFIGURATION -------#
#define LEFT_DIR_PIN 3
#define LEFT_STEP_PIN 46
#define LEFT_EN_PIN 9
#define LEFT_STEPS_PER_REV 400

#define RIGHT_DIR_PIN 21
#define RIGHT_STEP_PIN 47
#define RIGHT_EN_PIN 48
#define RIGHT_STEPS_PER_REV 400

#define WHEEL_DIAMETER_MM 60.0f
#define WHEEL_BASE_MM 132.0f

#define MAX_LINEAR_SPEED_MM_PER_S 10
#define MAX_ANGULAR_SPEED_RAD_PER_S 1.0

// #------- PID CONFIGURATION -------#
#define LINEAR_SPEED_KP 0.0f
#define LINEAR_SPEED_KI 0.0f
#define LINEAR_SPEED_KD 0.0f

#define ANGULAR_SPEED_KP 0.0f
#define ANGULAR_SPEED_KI 0.0f
#define ANGULAR_SPEED_KD 0.0f

#define LINEAR_DISTANCE_KP 10.0f
#define LINEAR_DISTANCE_KI 0.0f
#define LINEAR_DISTANCE_KD 0.0f

#define ANGULAR_DISTANCE_KP 10.0f
#define ANGULAR_DISTANCE_KI 0.0f
#define ANGULAR_DISTANCE_KD 0.0f


// #------- LORA CONFIGURATION -------#
#define SS 10 // NSS pin
#define RST 16 // RESET pin
#define BUSY 15 // BUSY pin
// #define SX126X_SPI_FREQUENCY  1000000 // SPI frequency for SX126x

// ESP XIAO DEVKIT PINOUT
// #define SS 4 // NSS pin
// #define RST 3 // RESET pin
// #define BUSY 2 // BUSY pin

// #-------- DEV CONFIGURATION ---------#
#define ENABLE_OTA false
#define ENABLE_LORA false

