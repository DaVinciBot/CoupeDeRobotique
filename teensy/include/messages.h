#pragma pack(1)
// dans nos structures, nous avons des variables plus petites que la taille
// défaut du processeur (processeur 32 bits et variables 8 bits de type byte)
// cela indique au compilateur de ne pas ajouter de padding entre les variables
// (pack(1) indique que la taille de l'alignement est de 1 octet)

#include <Arduino.h>

struct msg_Go_To
{
    byte command = GO_TO;
    float x;
    float y;
    bool is_forward;
    byte max_speed;
    uint16_t next_position_delay;
    uint16_t action_error_auth;
    uint16_t traj_precision;
    byte correction_trajectory_speed;
    byte acceleration_start_speed;
    float acceleration_distance;
    byte deceleration_end_speed;
    float deceleration_distance;
    byte id_Go_To;
};

struct msg_Curve_Go_To
{
    byte command = CURVE_GO_TO;
    float target_x;
    float target_y;
    float center_x;
    float center_y;
    unsigned short interval;
    bool direction;
    byte speed;
    uint16_t next_position_delay;
    uint16_t action_error_auth;
    uint16_t traj_precision;
};

struct msg_Keep_Current_Position
{
    byte command = KEEP_CURRENT_POSITION;
};

struct msg_Disable_Pid
{
    byte command = DISABLE_PID;
};
struct msg_Enable_Pid
{
    byte command = ENABLE_PID;
};

struct msg_Update_Position
{
    byte command = UPDATE_POSITION;
    float x;
    float y;
    float theta;
};

struct msg_Set_Home
{
    byte command = SET_HOME;
    float x;
    float y;
    float theta;
};

struct msg_Action_Finished
{
    byte command = ACTION_FINISHED;
    byte action_id;
};

struct msg_GoTo_Finished
{
    byte command = GOTO_FINISHED;
    byte goto_id;
}

struct msg_Set_PID
{
    byte command = SET_PID;
    float kp;
    float ki;
    float kd;
};

struct msg_String
{
    byte command = STRING;
    char str[249]; // Max size is 256 - 6 (Intercom) - 1 (cmd ID)
};