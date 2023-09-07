#pragma pack(1)
// dans nos structures, nous avons des variables plus petites que la taille
// défaut du processeur (processeur 32 bits et variables 8 bits de type byte)
// cela indique au compilateur de ne pas ajouter de padding entre les variables
// (pack(1) indique que la taille de l'alignement est de 1 octet)

#include <Arduino.h>

struct msg_Go_To {
    byte command = GO_TO;
    float x;
    float y;
    bool is_forward;
    byte speed;
    uint16_t next_position_delay;
    uint16_t action_error_auth;
    uint16_t traj_precision;
};

struct msg_Update_Position {
    byte command = UPDATE_POSITION;
    float x;
    float y;
    float theta;
};