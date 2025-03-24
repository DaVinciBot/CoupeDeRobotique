#pragma pack(1)
// dans nos structures, nous avons des variables plus petites que la taille
// défaut du processeur (processeur 32 bits et variables 8 bits de type byte)
// cela indique au compilateur de ne pas ajouter de padding entre les variables
// (pack(1) indique que la taille de l'alignement est de 1 octet)

#include <Arduino.h>

// ====== USB Communication Signature ======
// This signature must be exactly the same on both sides (Raspberry Pi and Teensy) to ensure valid communication.
const byte END_BYTES_SIGNATURE[4] = {0xBA, 0xDD, 0x1C, 0xC5};

// ====== Message Types ======
/* Definition of message IDs */
// rasp -> teensy : 0-127 (Convention)

// Rolling Basis
#define SET_SPEED_AND_POSITION 0
#define SET_PID 1
#define SET_ODOMETRIE 2

// Actuators
#define SET_SERVO_ANGLE 3
#define STEPPER_STEP 4
#define SET_SERVO_ANGLE_DETACH 5
#define ATTACH_SWITCH 6

// Init Message
#define INIT_TEENSY 125

// Common (Rolling Basis + Actuators)
#define RESET_TEENSY 126

// two ways : 127 (Convention)
#define NACK 127

// teensy -> rasp : 128-255 (Convention)
// Rolling Basis
#define UPDATE_ROLLING_BASIS 128

// Actuators
#define SWITCH_STATE_RETURN 129

// Common (Rolling Basis + Actuators)
#define PRINT 254
#define UNKNOWN_MSG_TYPE 255

/* Definition of the messages content */
// rasp -> teensy : 0-127

// Rolling Basis
struct msg_set_speed_and_position
{
    byte command = SET_SPEED_AND_POSITION;
    float target_linear_speed;
    float target_angular_speed;
    float target_position_x;
    float target_position_y;
    float target_position_theta;
};

struct msg_set_pid
{
    byte command = SET_PID;
    byte pid_type;
    float kp;
    float ki;
    float kd;
};

struct msg_set_odometrie
{
    byte command = SET_ODOMETRIE;
    float x;
    float y;
    float theta;
};

// Actuators
struct msg_set_servo_angle
{
    byte command = SET_SERVO_ANGLE;
    byte pin;   // pin to which the servo is connected
    byte angle; // angle to which the servo should be moved in degrees
};

struct msg_set_servo_angle_detach
{
    byte command = SET_SERVO_ANGLE_DETACH;
    byte pin;         // pin to which the servo is connected
    byte angle;       // angle to which the servo should be moved in degrees
    int detach_delay; // delay in milliseconds before detaching the servo
};

struct msg_stepper_step
{
    byte command = STEPPER_STEP;
    int steps;       // total number of steps this motor can take
    bool dir;        // direction of the motor
    int speed;       // speed
    byte pin_dir;    // pin to which the direction pin is connected
    byte pin_step;   // pin to which the step pin is connected
    byte pin_driver; // pin to which the driver pin is connected
};

struct msg_attach_switch
{
    byte command = ATTACH_SWITCH;
    byte pin; // pin to which the servo is connected
};

// Common (Rolling Basis + Actuators)
struct msg_reset_teensy
{
    byte command = RESET_TEENSY;
};

// teensy -> rasp : 128-255

// Rolling Basis
struct msg_update_rolling_basis
{
    byte command = UPDATE_ROLLING_BASIS;
    float x;
    float y;
    float theta;
    float current_linear_speed;
    float current_angular_speed;
};

// Actuators
struct msg_switch_state_return
{
    byte command = SWITCH_STATE_RETURN;
    byte pin;   // pin of the switch
    bool state; // switch state
};

// Common (Rolling Basis + Actuators)
struct msg_unknown_msg_type
{
    byte command = UNKNOWN_MSG_TYPE;
    byte type_id; // ID of the unknown message
};
