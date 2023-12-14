#include <Arduino.h>
#include <actions.h>
#include <pins.h>
//#include <Servo.h>

Com *com;

void (*functions[256])(byte *msg, byte size); // a tab a pointer to void functions

// Define a global array of Servo_Motor. Some name of variables are not allowed becaused they are used in Servo
int servo_pins[] = {SERVO1_PIN};
constexpr int nb_servos = sizeof(servo_pins)/sizeof(servo_pins[0]);
Servo_Motor s[nb_servos];

void call_servo_go_to(byte *msg, byte size)
{
    msg_Servo_Go_To *servo_go_to_msg = (msg_Servo_Go_To*) msg;
    bool lauched = false;
    for(int i=0; !lauched && i<nb_servos;i++)
    {
        if(s[i].pin==servo_go_to_msg->pin)
        {
          servo_go_to(s[i].actuator,servo_go_to_msg->angle);
          lauched = true;
        }
    }
}

void setup()
{
  com = new Com(&Serial, 115200);

  // only the messages received by the teensy are listed here
  functions[SERVO_GO_TO] = &call_servo_go_to;

  Serial.begin(115200);

  // Init Servos
  for(int i=0;i<nb_servos;i++)
  {
    s[i].actuator = new Servo();
    s[i].actuator->attach(servo_pins[i]);
    s[i].pin = servo_pins[i];
  }

}

void loop()
{

  // Com
  handle_callback(com);
}

/*

 This code was realized by Florian BARRE
    ____ __
   / __// /___<
  / _/ / // _ \
 /_/  /_/ \___/

*/
