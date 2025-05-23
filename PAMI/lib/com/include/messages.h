#pragma pack(1)
// dans nos structures, nous avons des variables plus petites que la taille
// défaut du processeur (processeur 32 bits et variables 8 bits de type byte)
// cela indique au compilateur de ne pas ajouter de padding entre les variables
// (pack(1) indique que la taille de l'alignement est de 1 octet)

#include <Arduino.h>

// ====== INTERCOM Communication Signature ======
// This signature must be exactly the same on ALL sides (Raspberry Pi and PAMI) to ensure valid communication.
const byte END_BYTES_SIGNATURE[4] = {0xBA, 0xDD, 0x1C, 0xC5};

// ====== Message Types ======
/* Definition of message IDs */
// rasp -> PAMI : 0-127 (Convention)

// PAMI
#define SET_POSITION 0
#define SET_PID 1
#define SET_ODOMETRIE 2
#define SET_SPEED 3

// Actuators
#define SET_SERVO_ANGLE 3

// Common (Teensy + ESP)
#define RESET_PAMI 126

// two ways : 127 (Convention)
#define NACK 127

// teensy -> rasp : 128-255 (Convention)
// PAMI
#define UPDATE_PAMI 128

// Actuators
#define ENABLE_ACTUATOR 129

// Common (Teensy + ESP)
#define PRINT 254
#define UNKNOWN_MSG_TYPE 255

/* Definition of the messages content */
// rasp -> teensy : 0-127

// Rolling Basis
struct msg_set_position
{
    byte command = SET_POSITION;
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
struct msg_set_speed
{
    byte command = SET_SPEED;
    float speed;
};

// Common (Rolling Basis + Actuators)
struct msg_reset_pami
{
    byte command = RESET_PAMI;
};

// teensy -> rasp : 128-255

// Rolling Basis
struct msg_update_pami
{
    byte command = UPDATE_PAMI;
    float x;
    float y;
    float theta;
};

// Common (Rolling Basis + Actuators)
struct msg_unknown_msg_type
{
    byte command = UNKNOWN_MSG_TYPE;
    byte type_id; // ID of the unknown message
};

struct msg_print
{
    byte command = PRINT;
    char message[252];
};