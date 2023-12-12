#include <Arduino.h>
//#include <com.h>
#include <messages.h>
#include <pins.h>
#include <Servo.h>

//#include <servo_motor.h>

Com *com;

void (*functions[256])(byte *msg, byte size); // a tab a pointer to void functions

int servo_pins[] = {SERVO1_PIN}; // contains all servos' pin
const int m = sizeof(servo_pins);
Servo_Motor servos[m]; // a list 

void call_servo_go_to(byte *msg, byte size)
{
    msg_Servo_Go_To *servo_go_to_msg = (msg_Servo_Go_To*) msg;
    int m = sizeof(servos);
    bool lauched = false;
    for(int i=0; !lauched && i<m;i++)
    {
        if(servos[i].pin==servo_go_to_msg->pin)
        {
          servo_go_to(servos[i].actuator,servo_go_to_msg->angle);
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
  for(int i=0;i<m;i++)
  {
    Servo_Motor servo;
    servo.actuator = new Servo();
    servo.actuator->attach(servo_pins[i]);
    servo.pin = servo_pins[i];
    servos[i]=servo;
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
