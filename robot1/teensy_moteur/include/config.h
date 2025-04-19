/*
 * This file is dedicated to the configuration of the robot: all the constants and the pinout are defined here.
 */

// Default position
#define START_X 0.0
#define START_Y 1.0
#define START_THETA 0.0

// Motor Left
#define L_ENCA 12
#define L_ENCB 11
#define L_PWM 5
#define L_IN2 3
#define L_IN1 4

// Motor Right
#define R_ENCA 14 // Va te faire foutre (Flo)
#define R_ENCB 13 // Si rien ne marche change les pins
#define R_PWM 2
#define R_IN2 1
#define R_IN1 0

// Creation Rolling Basis
// Motor
#define MAX_PWM 180

// Encoder
#define ENCODER_RESOLUTION 2048
#define ENTRAXE 29.8
#define WHEEL_DIAMETER 5.8

// PIDs
#define KP_LINEAR_SPEED 30 // 30
#define KI_LINEAR_SPEED 0
#define KD_LINEAR_SPEED 0 // 0.005

#define KP_ANGULAR_SPEED 30 // 30
#define KI_ANGULAR_SPEED 0
#define KD_ANGULAR_SPEED 0

#define KP_LINEAR_DISTANCE 0 // 20
#define KI_LINEAR_DISTANCE 0
#define KD_LINEAR_DISTANCE 0

#define KP_ANGULAR_DISTANCE 0 // 20
#define KI_ANGULAR_DISTANCE 0
#define KD_ANGULAR_DISTANCE 0

#define LINEAR_SPEED_PID_ID 0
#define ANGULAR_SPEED_PID_ID 1
#define LINEAR_POSITION_PID_ID 2
#define ANGULAR_POSITION_PID_ID 3

// PWM frequency
#define PWM_FREQUENCY 40000

// Asservissement echantillonage fréquence
#define ASSERVISSEMENT_FREQUENCY 10000

// Com baudrate
#define BAUDRATE 115200
