#include <Arduino.h>
#include <LiquidCrystal_I2C.h>
#include <actions.h>
#include <Servo.h>
#include <Bonezegei_A4988.h>
#include <config.h>

Com *com;

void *actuators[48] = {nullptr};
LiquidCrystal_I2C *lcd = nullptr;
void (*callback_functions[256])(byte *msg, byte size); // a tab a pointer to void functions

void call_servo_go_to(byte *msg, byte size)
{
  msg_Servo_Go_To *servo_go_to_msg = (msg_Servo_Go_To *)msg;
  if (actuators[servo_go_to_msg->pin] == nullptr)
  {
    Servo *servo = new Servo();
    servo->attach(servo_go_to_msg->pin);
    actuators[servo_go_to_msg->pin] = (void *)servo;
  }
  Servo *servo = (Servo *)actuators[servo_go_to_msg->pin];
  if (!servo->attached())
  {
    servo->attach(servo_go_to_msg->pin);
  }
  servo_go_to(servo, servo_go_to_msg->angle);
}

void call_servo_go_to_detach(byte *msg, byte size)
{
  msg_Servo_Go_To_Detach *servo_go_to_msg = (msg_Servo_Go_To_Detach *)msg;
  if (actuators[servo_go_to_msg->pin] == nullptr)
  {
    Servo *servo = new Servo();
    servo->attach(servo_go_to_msg->pin);
    actuators[servo_go_to_msg->pin] = (void *)servo;
  }
  Servo *servo = (Servo *)actuators[servo_go_to_msg->pin];
  if (!servo->attached())
  {
    servo->attach(servo_go_to_msg->pin);
  }
  servo_go_to(servo, servo_go_to_msg->angle);
  delay(servo_go_to_msg->detach_delay);
  (servo)->detach();
}

void call_stepper_step(byte *msg, byte size)
{
  msg_Stepper_Go_To *stepper_go_to_msg = (msg_Stepper_Go_To *)msg;
  if (actuators[stepper_go_to_msg->pin_dir] == nullptr)
  {
    Bonezegei_A4988 *stepper = new Bonezegei_A4988(
        stepper_go_to_msg->pin_dir,
        stepper_go_to_msg->pin_step);
    stepper->begin();
    actuators[stepper_go_to_msg->pin_dir] = (void *)stepper;
    pinMode(stepper_go_to_msg->pin_driver, OUTPUT);
  }
  Bonezegei_A4988 *stepper = (Bonezegei_A4988 *)actuators[stepper_go_to_msg->pin_dir];
  stepper->setSpeed(stepper_go_to_msg->speed);
  stepper_step(
      stepper,
      stepper_go_to_msg->steps,
      stepper_go_to_msg->dir,
      stepper_go_to_msg->pin_driver);
}

void lcd_init(byte *msg, byte size)
{
  msg_Lcd_Init *lcd_init_msg = (msg_Lcd_Init *)msg;
  lcd = new LiquidCrystal_I2C(lcd_init_msg->adress, lcd_init_msg->nb_col, lcd_init_msg->nb_line);
  lcd->init();
  lcd->backlight();
}

void call_lcd_print(byte *msg, byte size)
{
  msg_Lcd_Print *lcd_print_msg = (msg_Lcd_Print *)msg;
  lcd_print(lcd, String(lcd_print_msg->text));
}

void initilize_callback_functions()
{
  // only the messages received by the teensy are listed here
  callback_functions[SERVO_GO_TO] = &call_servo_go_to;
  callback_functions[STEPPER_STEP] = &call_stepper_step;
  callback_functions[SERVO_GO_TO_DETACH] = &call_servo_go_to_detach;
  callback_functions[LCD_INIT] = &lcd_init;
  callback_functions[LCD_PRINT] = &call_lcd_print;
}

void setup()
{
  com = new Com(&Serial, BAUDRATE);
  initilize_callback_functions();
  // digitalWrite(15, HIGH); // Immediatly disable driver on the stepper, to prevent heating. Dirty solution.
}

void loop()
{
  com->handle_callback(callback_functions);
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
