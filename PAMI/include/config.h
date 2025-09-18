#include <Arduino.h>
#include "lidar_pami.h"
#include "motor.h"
#include "navigation.h"
#include "rolling_basis.h"


// #------- GENERAL CONFIGURATION -------#
#define ACS_TRESHOLD 40  // Threshold for ACS activation in mm

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

#define K 8.0f

// #------- PID CONFIGURATION -------#
#define LINEAR_DISTANCE_KP 2000.0f
#define LINEAR_DISTANCE_KI 0.0f
#define LINEAR_DISTANCE_KD 0.0f

#define ANGULAR_DISTANCE_KP 1000.0f
#define ANGULAR_DISTANCE_KI 10000.0f
#define ANGULAR_DISTANCE_KD 0.0f

// #------- SERVO CONFIGURATION -------#
#define SERVO_PIN 42  // Servo pin

// #------- LORA CONFIGURATION -------#
#define SS 10    // NSS pin
#define RST 16   // RESET pin
#define BUSY 15  // BUSY pin

// #-------- DEV CONFIGURATION ---------#
#define ENABLE_OTA false
#define ENABLE_LORA false
