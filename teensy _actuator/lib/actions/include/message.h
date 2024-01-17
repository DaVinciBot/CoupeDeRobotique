#pragma pack(1)
// dans nos structures, nous avons des variables plus petites que la taille
// défaut du processeur (processeur 32 bits et variables 8 bits de type byte)
// cela indique au compilateur de ne pas ajouter de padding entre les variables
// (pack(1) indique que la taille de l'alignement est de 1 octet)

#include <Arduino.h>
#include <commands.h>

struct msg_Unknown_Msg_Type
{
    byte command = UNKNOWN_MSG_TYPE;
    byte type_id;
};

struct msg_Servo_Go_To
{
    byte command = SERVO_GO_TO;
    byte pin;
    byte angle;
};

struct msg_Ultrasonic_Read
{
    byte command = ULTRASONIC_READ;
    byte trigger_pin;
    byte echo_pin;
};

struct msg_Ultrasonic_Call_Back
{
    byte command = ULTRASONIC_CALL_BACK;
    byte distance;
};