/*
 * This file is dedicated to the configuration of the robot: all the constants and the pinout are defined here.
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
#define R_ENCA 14 // Va te faire foutre (Flo)
#define R_ENCB 13 // Si rien ne marche change les pins
#define R_PWM 2
#define R_IN2 1
#define R_IN1 0

// Creation Rolling Basis
// Motor
#define MAX_PWM 180

// Encoder
#define ENCODER_RESOLUTION 600
#define CENTER_DISTANCE 33.57
#define WHEEL_DIAMETER 6.1


// PIDs
#define KP_LINEAR_SPEED 20//30
#define KI_LINEAR_SPEED 0
#define KD_LINEAR_SPEED 0//0.005

#define KP_ANGULAR_SPEED 50//30
#define KI_ANGULAR_SPEED 0
#define KD_ANGULAR_SPEED 0

#define KP_LINEAR_DISTANCE 0//20
#define KI_LINEAR_DISTANCE 0
#define KD_LINEAR_DISTANCE 0

#define KP_ANGULAR_DISTANCE 0//20
#define KI_ANGULAR_DISTANCE 0
#define KD_ANGULAR_DISTANCE 0


// PWM frequency
#define PWM_FREQUENCY 40000

// Asservissement echantillonage fréquence 
#define ASSERVISSEMENT_FREQUENCY 10000

// Com baudrate
#define BAUDRATE 115200