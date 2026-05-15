#ifndef PAMI_CONFIG_H
#define PAMI_CONFIG_H

#include <Arduino.h>

// General configuration
#define ACS_TRESHOLD 40  // Threshold for ACS activation in mm
#define MICROSTEPPING_FACTOR 4

// Motor configuration
#define LEFT_DIR_PIN 3
#define LEFT_STEP_PIN 46
#define LEFT_EN_PIN 9
#define LEFT_STEPS_PER_REV 400 * MICROSTEPPING_FACTOR

#define RIGHT_DIR_PIN 21
#define RIGHT_STEP_PIN 47
#define RIGHT_EN_PIN 48
#define RIGHT_STEPS_PER_REV 400 * MICROSTEPPING_FACTOR

#define PULSE_US 500
#define WHEEL_DIAMETER_MM 60.01f
#define WHEEL_BASE_MM 200.0f

#define MAX_LINEAR_SPEED_MM_PER_S 40.0f
#define MAX_ANGULAR_SPEED_RAD_PER_S 1.0f
#define MOTOR_ACCELERATION_STEPS_PER_S2 1000.0f

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
#define LORA_BAUD 115200
#define LORA_M0_PIN -1
#define LORA_M1_PIN -1
#define LORA_AUX_PIN 4

// LIDAR configuration
#define LIDAR_RX_PIN 44
#define LIDAR_TX_PIN 43

// Development toggles
#define ENABLE_DEBUG false
#define ENABLE_OTA false
#define ENABLE_LORA false

#if ENABLE_DEBUG
#define DEBUG_PRINT(...) Serial.print(__VA_ARGS__)
#define DEBUG_PRINTLN(...) Serial.println(__VA_ARGS__)
#define DEBUG_PRINTF(...) Serial.printf(__VA_ARGS__)
#else
#define DEBUG_PRINT(...) ((void)0)
#define DEBUG_PRINTLN(...) ((void)0)
#define DEBUG_PRINTF(...) ((void)0)
#endif

// OTA Wi-Fi credentials
#define OTA_WIFI_SSID "DVB"
#define OTA_WIFI_PASSWORD "davincibot"
#define OTA_HOSTNAME "pami"
#define OTA_FALLBACK_AP_SSID "PAMI-OTA"
#define OTA_FALLBACK_AP_PASSWORD "pami-ota"

#endif
