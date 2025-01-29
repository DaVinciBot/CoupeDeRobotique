#pragma pack(1)
// dans nos structures, nous avons des variables plus petites que la taille
// défaut du processeur (processeur 32 bits et variables 8 bits de type byte)
// cela indique au compilateur de ne pas ajouter de padding entre les variables
// (pack(1) indique que la taille de l'alignement est de 1 octet)

#include <Arduino.h>

/* Definition of message IDs */
// rasp -> teensy : 0-127 (Convention)
#define SET_SPEED_AND_POSITION 0
#define SET_PID 1

// two ways : 127 (Convention)
#define NACK 127

// teensy -> rasp : 128-255 (Convention)
#define PRINT 128
#define UPDATE_ROLLING_BASIS 129
#define UNKNOWN_MSG_TYPE 255

/* Definition of the messages content */
// rasp -> teensy : 0-127
struct msg_set_speed_and_position
{
    byte command = SET_SPEED_AND_POSITION;
    float target_linear_speed;
    float target_angular_speed;
    float target_position_x;
    float target_position_y;
    float target_position_theta;
};

// teensy -> rasp : 128-255
struct msg_update_rolling_basis
{
    byte command = UPDATE_ROLLING_BASIS;
    float x;
    float y;
    float theta;
    float current_linear_speed;
    float current_angular_speed;
};

struct msg_set_pid
{
    byte command = SET_PID;
    byte pid_type;
    float kp;
    float ki;
    float kd;
};

struct msg_unknown_msg_type
{
    byte command = UNKNOWN_MSG_TYPE;
    byte type_id; // ID of the unknown message
};
