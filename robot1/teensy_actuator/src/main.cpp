// Externe libraries used: Arduino, TimerOne, ATOMIC
#include <Arduino.h>          // Arduino framework
#include <Servo.h>            // Servo object to control the servomotors
#include <Bonezegei_A4988.h>  // Bonezegei_A4988 object to control the stepper motors

// Custom libraries used: Com
#include <com.h> // Communication object to manage the communication between the teensy and the Raspberry Pi

// Configuration file (contains all the constants and pinout), it is just a main.cpp header file
#include <config.h>

// 1. Define the actuators tabs (pointers tab)
void *actuators[48] = {nullptr};
bool switch_pins[48] = {false};

// 2. Instanciate the Communication object
Com *com;

// 3. Define all com callback functions
// a. define the callback functions
void set_servo_angle(byte *msg, byte size)
{
  msg_set_servo_angle *servo_set_servo_angle_msg = (msg_set_servo_angle *)msg;
  if (actuators[servo_set_servo_angle_msg->pin] == nullptr)
  {
    Servo *servo = new Servo();
    servo->attach(servo_set_servo_angle_msg->pin);
    actuators[servo_set_servo_angle_msg->pin] = (void *)servo;
  }
  Servo *servo = (Servo *)actuators[servo_set_servo_angle_msg->pin];
  if (!servo->attached())
  {
    servo->attach(servo_set_servo_angle_msg->pin);
  }
  servo->write(servo_set_servo_angle_msg->angle);
}

void set_servo_angle_detach(byte *msg, byte size)
{
  msg_set_servo_angle_detach *servo_angle_detach_msg = (set_servo_angle_detach *)msg;
  if (actuators[servo_angle_detach_msg->pin] == nullptr)
  {
    Servo *servo = new Servo();
    servo->attach(servo_angle_detach_msg->pin);
    actuators[servo_angle_detach_msg->pin] = (void *)servo;
  }
  Servo *servo = (Servo *)actuators[servo_angle_detach_msg->pin];
  if (!servo->attached())
  {
    servo->attach(servo_angle_detach_msg->pin);
  }
  servo->write(servo_angle_detach_msg->angle);
  delay(servo_angle_detach_msg->detach_delay);
  servo->detach();
}

void stepper_step(byte *msg, byte size)
{
  msg_stepper_step *stepper_step_msg = (msg_stepper_step *)msg;
  if (actuators[stepper_step_msg->pin_dir] == nullptr)
  {
    Bonezegei_A4988 *stepper = new Bonezegei_A4988(
      stepper_step_msg->pin_dir,
      stepper_step_msg->pin_step);
    stepper->begin();
    actuators[stepper_step_msg->pin_dir] = (void *)stepper;
    pinMode(stepper_step_msg->pin_driver, OUTPUT);
  }
  Bonezegei_A4988 *stepper = (Bonezegei_A4988 *)actuators[stepper_step_msg->pin_dir];
  stepper->setSpeed(stepper_step_msg->speed);

  // Step the motor
  digitalWrite(stepper_step_msg->pin_driver, LOW);
  if (stepper_step_msg->dir)
      stepper->step(1, steps);
  else
      stepper->step(0, steps);
  digitalWrite(stepper_step_msg->pin_driver, HIGH);
}

void attach_switch(byte *msg, byte size)
{
  msg_attach_switch *attach_switch_msg = (msg_attach_switch *)msg;
  switch_pins[attach_switch_msg->pin] = true;
  // Define switch as input
  pinMode(attach_switch_msg->pin, INPUT);
  // Read the switch state
  actuators[attach_switch_msg->pin] = (void *)(digitalRead(attach_switch_msg->pin));

  // Send to the rasp the current state of the switch
  msg_switch_state_return switch_state_return_msg;
  switch_state_return_msg.pin = attach_switch_msg->pin;
  switch_state_return_msg.state = (bool)actuators[attach_switch_msg->pin];
  com->send_msg((byte *)&switch_state_return_msg, sizeof(msg_switch_state_return));
}

// b. assign the callback functions to the right message id
void (*callback_functions[256])(byte *msg, byte size);

void initilize_callback_functions()
{
  callback_functions[SET_SERVO_ANGLE] = &set_servo_angle;
  callback_functions[STEPPER_STEP] = &stepper_step;
  callback_functions[SET_SERVO_ANGLE_DETACH] = &set_servo_angle_detach;
  callback_functions[ATTACH_SWITCH] = &attach_switch;
}

void setup()
{
  com = new Com(&Serial, BAUDRATE);

  // Initialize callback functions
  initialize_callback_functions();
  // digitalWrite(15, HIGH); // Immediatly disable driver on the stepper, to prevent heating. Dirty solution.
}

void loop()
{
  com->handle_callback(callback_functions);

  // Check the switch state
  for (int i = 0; i < 48; i++)
  {
    if (switch_pins[i])
    {
      bool state = digitalRead(i);
      if (state != (bool)actuators[i])
      {
        actuators[i] = (void *)state;
        msg_switch_state_return switch_state_return_msg;
        switch_state_return_msg.pin = i;
        switch_state_return_msg.state = state;
        com->send_msg((byte *)&switch_state_return_msg, sizeof(msg_switch_state_return));
      }
    }
  }
}

/*

 This code was realized by Romain CUCHET
__________                      .__         _________
\______   \ ____   _____ _____  |__| ____   \_   ___ \
 |       _//  _ \ /     \\__  \ |  |/    \  /    \  \/   
 |    |   (  <_> )  Y Y  \/ __ \|  |   |  \ \     \____
 |____|_  /\____/|__|_|  (____  /__|___|  /  \______  /
        \/             \/     \/        \/          \/

*/
