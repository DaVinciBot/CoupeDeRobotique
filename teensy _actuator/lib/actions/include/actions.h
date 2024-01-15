#include <servo_motor.h>
#include <Servo.h>
#include <com.h>
#include <message.h>

extern void (*functions[256])(byte *msg, byte size);
extern void handle_callback(Com *com);
extern void servo_go_to(Servo* servo, int angle);

