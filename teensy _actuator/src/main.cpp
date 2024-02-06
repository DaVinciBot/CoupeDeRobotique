#include <actions.h>
#include <pins.h>
//#include <Servo.h>

Com *com;

void (*functions[256])(byte *msg, byte size); // a tab a pointer to void functions

// Define an array of Servo_Motor (max = 12). Some name of variables are not allowed becaused they are used in Servo
int servo_pins[] = {SERVO1_PIN};
constexpr int nb_servos = sizeof(servo_pins)/sizeof(servo_pins[0]);
Servo_Motor s[nb_servos];

// Define an array of Ultrasonic 
int trigger_pins[] = {TRIGGER1_PIN}; // index must correspond to echo_pins ones
int echo_pins[] = {ECHO1_PIN}; // index must correspond to trigger_pins ones
constexpr int nb_ultrasonic = sizeof(trigger_pins)/sizeof(trigger_pins[0]);
Ultrasonic_Sensor u[nb_ultrasonic];

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

void call_read_ultrasonic(byte *msg, byte size)
{
    msg_Ultrasonic_Read *servo_ultrasonic_msg = (msg_Ultrasonic_Read*) msg;
    bool lauched = false;
    for(int i=0; !lauched && i<nb_ultrasonic;i++)
    {
        if(u[i].trigger_pin==servo_ultrasonic_msg->trigger_pin && u[i].echo_pin==servo_ultrasonic_msg->echo_pin )
        {
          msg_Ultrasonic_Call_Back msg = ultrasonic_read(u[i].actuator);
          com->send_msg((byte *)&msg, sizeof(msg_Ultrasonic_Call_Back));
          lauched = true;
        }
    }
}

void setup()
{
  com = new Com(&Serial, 115200);

  // only the messages received by the teensy are listed here
  functions[SERVO_GO_TO] = &call_servo_go_to;
  functions[ULTRASONIC_READ] = &call_read_ultrasonic;

  Serial.begin(115200);

  // Init Servos
  for(int i=0;i<nb_servos;i++)
  {
    s[i].actuator = new Servo();
    s[i].actuator->attach(servo_pins[i]);
    s[i].pin = servo_pins[i];
  }

  // Init Ultrasonics
  for(int i=0;i<nb_ultrasonic;i++)
  {
    u[i].actuator = new Ultrasonic(trigger_pins[i],echo_pins[i]);
    u[i].trigger_pin = trigger_pins[i];
    u[i].echo_pin = echo_pins[i];
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
