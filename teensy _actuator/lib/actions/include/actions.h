#include <servo_motor.h>
#include <Servo.h>
#include <com.h>
#define SERVO_GO_TO 1
#define UNKNOWN_MSG_TYPE 255

extern void (*functions[256])(byte *msg, byte size);
extern void handle_callback(Com *com);
extern void servo_go_to(byte *msg, byte size, Servo_Motor servos[]);

