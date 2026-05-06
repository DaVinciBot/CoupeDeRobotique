/*
 * This file is dedicated to the configuration of the robot: all the constants
 * and the pinout are defined here.
 */

// Default position
#define START_X 0.0
#define START_Y 0.0
#define START_THETA 0.0

// Motor Left
#define L_ENCA 12
#define L_ENCB 11
#define L_PWM 5
#define L_IN2 3
#define L_IN1 4

// Motor Right
#define R_ENCA 14  // Va te faire foutre (Flo)
#define R_ENCB 13  // Si rien ne marche change les pins
#define R_PWM 2
#define R_IN2 1
#define R_IN1 0

// Creation Rolling Basis
// Motor
#define MAX_PWM 240

// Encoder
#define ENCODER_RESOLUTION 1024
#define ENTRAXE 30.9
#define LEFT_WHEEL_DIAMETER 6.1
#define RIGHT_WHEEL_DIAMETER 5.9

// PIDs (position supervision)
#define KP_LINEAR_POSITION 0.8
#define KI_LINEAR_POSITION 0.0
#define KD_LINEAR_POSITION 0.0

#define KP_ANGULAR_POSITION 2.0
#define KI_ANGULAR_POSITION 0.0
#define KD_ANGULAR_POSITION 0.0

// PIDs (wheel position control)
#define KP_LEFT_WHEEL_POSITION 0.0
#define KI_LEFT_WHEEL_POSITION 0.0
#define KD_LEFT_WHEEL_POSITION 0.0

#define KP_RIGHT_WHEEL_POSITION 0.0
#define KI_RIGHT_WHEEL_POSITION 0.0
#define KD_RIGHT_WHEEL_POSITION 0.0

#define MIN_PWM_WHEEL 30

#define POSITION_MAX_LINEAR_STEP_CM 0.8
#define POSITION_MAX_ANGULAR_STEP_CM 0.8
#define POSITION_LINEAR_DEADBAND 0.0
#define POSITION_ANGULAR_DEADBAND 0.0

#define WHEEL_POSITION_MAX_PWM 240
#define WHEEL_POSITION_DEADBAND_CM 0.0

#define LINEAR_POSITION_PID_ID 0
#define ANGULAR_POSITION_PID_ID 1
#define LEFT_WHEEL_POSITION_PID_ID 2
#define RIGHT_WHEEL_POSITION_PID_ID 3

// PWM frequency
#define PWM_FREQUENCY 40000

// Asservissement echantillonage fréquence
#define ASSERVISSEMENT_FREQUENCY 5000

// Com baudrate
#define BAUDRATE 115200
