#ifndef PAMI_CONFIG_H
#define PAMI_CONFIG_H

#include <Arduino.h>

// General configuration
#define ACS_TRESHOLD 40  // Threshold for ACS activation in mm

// Motor configuration
#define LEFT_DIR_PIN 3
#define LEFT_STEP_PIN 46
#define LEFT_EN_PIN 9
#define LEFT_STEPS_PER_REV 400

#define RIGHT_DIR_PIN 21
#define RIGHT_STEP_PIN 47
#define RIGHT_EN_PIN 48
#define RIGHT_STEPS_PER_REV 400

#define PULSE_US 500
#define WHEEL_DIAMETER_MM 62.0f
#define WHEEL_BASE_MM 132.0f

#define MAX_LINEAR_SPEED_MM_PER_S 57.5f
#define MAX_ANGULAR_SPEED_RAD_PER_S 1.38f
#define MOTOR_ACCELERATION_STEPS_PER_S2 1000.0f

// Calibration
#define DISTANCE_CALIBRATION_FACTOR 0.4f
#define ANGULAR_CALIBRATION_FACTOR 0.9f

// PID configuration
#define LINEAR_DISTANCE_KP 2000.0f
#define LINEAR_DISTANCE_KI 0.0f
#define LINEAR_DISTANCE_KD 0.0f

#define ANGULAR_DISTANCE_KP 1000.0f
#define ANGULAR_DISTANCE_KI 10000.0f
#define ANGULAR_DISTANCE_KD 0.0f

// Servo configuration
#define SERVO_PIN 42

// LoRa configuration
#define LORA_RX_PIN 16
#define LORA_TX_PIN 17
#define LORA_BAUD 9600
#define LORA_M0_PIN -1
#define LORA_M1_PIN -1
#define LORA_AUX_PIN 4

// Development toggles
#define ENABLE_OTA false
#define ENABLE_LORA false

#endif
