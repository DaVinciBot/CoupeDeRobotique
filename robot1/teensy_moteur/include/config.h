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
#define R_ENCA 13  // Va te faire foutre (Flo)
#define R_ENCB 14  // Si rien ne marche change les pins
#define R_PWM 2
#define R_IN2 1
#define R_IN1 0

// Creation Rolling Basis
// Motor
#define MAX_PWM 240

// Encoder
#define ENCODER_RESOLUTION 1024
#define ENTRAXE 29.5
#define WHEEL_DIAMETER 5.9

#define M_S_TO_CM_S 100.0

// PIDs (velocity control)
// #define KP_LINEAR_VELOCITY 1.2
// #define KI_LINEAR_VELOCITY 0.02
// #define KD_LINEAR_VELOCITY 0.10

// #define KP_ANGULAR_VELOCITY 4.0
// #define KI_ANGULAR_VELOCITY 0.1
// #define KD_ANGULAR_VELOCITY 0.20
#define KP_LINEAR_VELOCITY 10.0
#define KI_LINEAR_VELOCITY 2.0
#define KD_LINEAR_VELOCITY 0.0

#define KP_ANGULAR_VELOCITY 4.0
#define KI_ANGULAR_VELOCITY 0.1
#define KD_ANGULAR_VELOCITY 0.2

// PIDs (position control)
#define KP_LINEAR_POSITION 0.8
#define KI_LINEAR_POSITION 0.0
#define KD_LINEAR_POSITION 0.0

#define KP_ANGULAR_POSITION 2.0
#define KI_ANGULAR_POSITION 0.0
#define KD_ANGULAR_POSITION 0.0

#define MIN_PWM_LINEAR 30
#define MIN_PWM_ANGULAR 60
#define LINEAR_FF_PWM_PER_CM_S 6.0
#define ANGULAR_FF_PWM_PER_RAD_S 35.0

#define COMMAND_TIMEOUT_US 100000
#define LINEAR_VELOCITY_ZERO_EPS 0.5
#define ANGULAR_VELOCITY_ZERO_EPS 0.02

#define HOLD_VEL_DEADBAND_LINEAR 0.05
#define HOLD_VEL_DEADBAND_ANGULAR 0.005
#define HOLD_VEL_MAX_PWM 140

#define POSITION_MAX_LINEAR_CM_S 30.0
#define POSITION_MAX_ANGULAR_RAD_S 2.0
#define POSITION_LINEAR_DEADBAND 0.0
#define POSITION_ANGULAR_DEADBAND 0.0

// Encoder-based velocity estimation
#define ENCODER_PPR 1024
#define MOTOR_VEL_ALPHA 0.25
#define MOTOR_VEL_MIN_TICKS 3
#define MOTOR_NO_TICK_TIMEOUT_US 80000
#define MAX_RPM_AMT10 7500.0

#define LINEAR_VELOCITY_PID_ID 0
#define ANGULAR_VELOCITY_PID_ID 1
#define LINEAR_POSITION_PID_ID 2
#define ANGULAR_POSITION_PID_ID 3

#define CONTROL_MODE_VELOCITY 0
#define CONTROL_MODE_POSITION 1

// PWM frequency
#define PWM_FREQUENCY 40000

// Asservissement echantillonage fréquence
#define ASSERVISSEMENT_FREQUENCY 5000

// Com baudrate
#define BAUDRATE 115200
