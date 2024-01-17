#include <servo_motor.h>
#include <ultrasonic_sensor.h>
#include <Servo.h>
#include <com.h>
#include <message.h>
#include <Arduino.h>

extern void (*functions[256])(byte *msg, byte size);
extern void handle_callback(Com *com);
extern void servo_go_to(Servo* servo, int angle);
extern void ultrasonic_read(Ultrasonic* ultrasonic,Com *com);

