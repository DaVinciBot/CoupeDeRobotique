#include <Arduino.h>
#include "lidar_pami.h"
#include "motor.h"
#include "navigation.h"
#include "rolling_basis.h"

// #------- GENERAL CONFIGURATION -------#
#define ACS_TRESHOLD 40  // Threshold for ACS activation in mm

// #------- MOTOR CONFIGURATION -------#
#define LEFT_DIR_PIN 3         // Direction pin for left motor
#define LEFT_STEP_PIN 46        // Step pin for left motor
#define LEFT_EN_PIN 9          // Enable pin for left motor 
#define LEFT_STEPS_PER_REV 400  // Steps per revolution for left motor

#define RIGHT_DIR_PIN 21         // Direction pin for right motor
#define RIGHT_STEP_PIN 47        // Step pin for right motor
#define RIGHT_EN_PIN 48          // Enable pin for right motor
#define RIGHT_STEPS_PER_REV 400  // Steps per revolution for right motor

#define PULSE_US 500             // Pulse width in microseconds for motor steps
#define WHEEL_DIAMETER_MM 62.0f  // Wheel diameter in mm
#define WHEEL_BASE_MM 132.0f     // Distance between the two wheels in mm

#define MAX_LINEAR_SPEED_MM_PER_S 10     // Maximum linear speed in mm/s
#define MAX_ANGULAR_SPEED_RAD_PER_S 1.0  // Maximum angular speed in rad/s

// #------- PID CONFIGURATION -------#
#define LINEAR_DISTANCE_KP 2000.0f  // Proportional gain for linear distance
#define LINEAR_DISTANCE_KI 0.0f     // Integral gain for linear distance
#define LINEAR_DISTANCE_KD 0.0f     // Derivative gain for linear distance

#define ANGULAR_DISTANCE_KP 1000.0f   // Proportional gain for angular distance
#define ANGULAR_DISTANCE_KI 10000.0f  // Integral gain for angular distance
#define ANGULAR_DISTANCE_KD 0.0f      // Derivative gain for angular distance

// #------- SERVO CONFIGURATION -------#
#define SERVO_PIN 42  // Servo pin

// #------- LORA CONFIGURATION (DX-LR01 UART) -------#
#define LORA_RX_PIN 16   // RX2 - TXD du module DX-LR01
#define LORA_TX_PIN 17   // TX2 - RXD du module DX-LR01
#define LORA_BAUD 9600   // Baud rate du DX-LR01
#define LORA_M0_PIN -1   // Mode pin M0 (connecté à GND = mode normal)
#define LORA_M1_PIN -1   // Mode pin M1 (connecté à GND = mode normal)
#define LORA_AUX_PIN 4  // AUX pin (non utilisé pour ce test)

// #-------- DEV CONFIGURATION ---------#
#define ENABLE_OTA false   // Enable OTA updates
#define ENABLE_LORA true   // Enable LoRa communication (DX-LR01 - UART based)
