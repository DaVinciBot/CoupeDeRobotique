#include <servo_motor.h>
#include <ultrasonic_sensor.h>
#include <Servo.h>
#include <com.h>
#include <message.h>
#include <Arduino.h>

extern void (*functions[256])(byte *msg, byte size);
void handle_callback(Com *com);
void servo_go_to(Servo* servo, int angle);
msg_Ultrasonic_Call_Back ultrasonic_read(Ultrasonic* ultrasonic);

