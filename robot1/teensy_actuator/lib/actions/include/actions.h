#include <Servo.h>
#include <com.h>
#include <message.h>
#include <Bonezegei_A4988.h>
#include <LiquidCrystal_I2C.h>

extern void (*functions[256])(byte *msg, byte size);
extern void handle_callback(Com *com);
extern void servo_go_to(Servo *servo, int angle);
extern void stepper_step(Bonezegei_A4988 *stepper, int steps, bool dir, byte pin_driver);
extern void lcd_print(LiquidCrystal_I2C *lcd, char *text);
