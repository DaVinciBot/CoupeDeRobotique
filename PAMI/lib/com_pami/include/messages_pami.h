/**
 * @brief Message IDs and payload structures used for inter-board
 *        communication between the Raspberry Pi and the PAMI controller.
 *
 * Conventions:
 *
 * - IDs 0..127: messages sent from Raspberry Pi to the controller (rasp ->
 * PAMI)
 *
 * - IDs 128..255: messages sent from the controller to Raspberry Pi (PAMI ->
 * rasp)
 */

#ifndef MESSAGES_PAMI_H
#define MESSAGES_PAMI_H

#pragma pack(1)
// Structures use 1-byte packing so that fields are laid out without
// padding. This ensures the wire-format matches across platforms.

#include <Arduino.h>

/**
 * @brief Fixed signature bytes used to validate frames on the wire.
 *
 * All devices must use the same signature to accept messages as valid.
 */
const byte END_BYTES_SIGNATURE[4] = {0xBA, 0xDD, 0x1C, 0xC5};

// ====== Message IDs ======
// rasp -> teensy : 0-127

// PAMI
#define SET_POSITION 0   // Message ID for Set target pose for rolling base
#define SET_PID 1        // Message ID for Set PID parameters
#define SET_ODOMETRIE 2  // Message ID for Set odometry (pose)
#define SET_SPEED 3      // Message ID for Set speed parameter

// Actuators
#define SET_SERVO_ANGLE 3  // Message ID for Set servo angle

// Common
#define RESET_PAMI 126  // Message ID for Reset PAMI
#define NACK 127        // Message ID for Negative acknowledgement

// teensy -> rasp : 128-255

// PAMI
#define UPDATE_PAMI 128      // Message ID for Periodic update containing pose
#define ENABLE_ACTUATOR 129  // Message ID Enable actuator command

// Common / Diagnostic
#define PRINT 254             // Message ID for Print text message
#define UNKNOWN_MSG_TYPE 255  // Message ID for Unknown message type indicator

// ====== Payload structures (packed) ======

/**
 * @brief Command: set target position and heading.
 *
 * Units: x,y = millimetres, theta = radians.
 */
struct msg_set_position {
    byte command = SET_POSITION;  // Message ID
    float target_position_x;      // X target (mm)
    float target_position_y;      // Y target (mm)
    float target_position_theta;  // Theta target (rad)
};

/**
 * @brief Command: set PID parameters for a named PID controller.
 *
 * pid_type is application-specific (e.g., 0 = linear, 1 = angular).
 */
struct msg_set_pid {
    byte command = SET_PID;  // Message ID
    byte pid_type;           // PID index/type
    float kp;                // Proportional gain
    float ki;                // Integral gain
    float kd;                // Derivative gain
};

/**
 * @brief Command: directly set the estimated odometry.
 */
struct msg_set_odometrie {
    byte command = SET_ODOMETRIE;  // Message ID
    float x;                       // X (mm)
    float y;                       // Y (mm)
    float theta;                   // Theta (rad)
};

/**
 * @brief Command: set a generic speed value. Interpretation depends on
 * the receiving subsystem.
 */
struct msg_set_speed {
    byte command = SET_SPEED;  // Message ID
    float speed;               // Speed value (units depend on consumer)
};

/**
 * @brief Common command: reset the PAMI controller.
 */
struct msg_reset_pami {
    byte command = RESET_PAMI;  // Message ID
};

/**
 * @brief Status update from PAMI containing current pose.
 */
struct msg_update_pami {
    byte command = UPDATE_PAMI;  // Message ID
    float x;                     // X (mm)
    float y;                     // Y (mm)
    float theta;                 // Theta (rad)
};

/**
 * @brief Notification: an unknown message type was received.
 */
struct msg_unknown_msg_type {
    byte command = UNKNOWN_MSG_TYPE;  // Message ID
    byte type_id;                     // Unknown message type ID
};

/**
 * @brief Diagnostic text message.
 *
 * The `message` field contains a C-string (null-terminated if it fits).
 */
struct msg_print {
    byte command = PRINT;  // Message ID
    char message[252];     // Text payload (max 251 chars + null)
};

#endif
