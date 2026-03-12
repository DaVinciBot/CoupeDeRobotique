#include "AtoB.h"
#include "action.h"
#include "actionneur.h"
#include "arduino_compat.h"
#include "carre.h"
#include "lidar_pami.h"
#include "motor.h"
#include "relative_forward.h"
#include "relative_turning.h"
#include "rolling_basis.h"
#include "triangle.h"

// #------- GENERAL CONFIGURATION -------#
#define ACS_TRESHOLD 40  // Threshold for ACS activation in mm

// #------- MOTOR CONFIGURATION -------#
#define LEFT_DIR_PIN 18         // Direction pin for left motor
#define LEFT_STEP_PIN 19        // Step pin for left motor
#define LEFT_EN_PIN 32          // Enable pin for left motor
#define LEFT_STEPS_PER_REV 400  // Steps per revolution for left motor

#define RIGHT_DIR_PIN 16         // Direction pin for right motor
#define RIGHT_STEP_PIN 17        // Step pin for right motor
#define RIGHT_EN_PIN 33          // Enable pin for right motor
#define RIGHT_STEPS_PER_REV 400  // Steps per revolution for right motor

#define PULSE_US 500             // Pulse width in microseconds for motor steps
#define WHEEL_DIAMETER_MM 60.0f  // Wheel diameter in mm
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

// #------- LORA CONFIGURATION -------#
#define SS 10    // NSS pin
#define RST 16   // RESET pin
#define BUSY 15  // BUSY pin

// #-------- DEV CONFIGURATION ---------#
#define ENABLE_OTA false   // Enable OTA updates
#define ENABLE_LORA false  // Enable LoRa communication

// #------- ROBOT ID -------#

#define ID_ROBOT 1
// Give an identification to each pami (going 1 to 6)
// to do it manually for each pami
#ifndef ID_ROBOT
#error "ID_ROBOT is not define "
#endif

// #------- OBSTACLE CONFIGURATION -------#
#define OBSTACLE_FRONT_THRESHOLD_MM \
    100  // Distance devant pour détecter un obstacle
#define OBSTACLE_RIGHT_THRESHOLD_MM \
    200  // Distance droite en dessous de laquelle la voie est bloquée
#define TURN_ANGLE_RAD 0.5f        // Angle de rotation droite en radians
#define REVERSE_DISTANCE_MM 80.0f  // Distance de recul avant de tourner
#define OBSTACLE_TIMEOUT_MS 3000   // Délai avant recul forcé (ms)

// Index des points lidar (sur 160 points, champ ~180°)
// Droite : points 120 à 159
#define SIDE_RIGHT_START 120
#define SIDE_RIGHT_END 159

// ------- ÉTAT D'ÉVITEMENT -------
enum AvoidState {
    AVOID_IDLE,       // Pas d'obstacle
    AVOID_WAITING,    // Obstacle devant, on attend que la droite se libère
    AVOID_REVERSING,  // Recul en cours (timeout dépassé)
    AVOID_TURNING,    // Rotation droite en cours
};
