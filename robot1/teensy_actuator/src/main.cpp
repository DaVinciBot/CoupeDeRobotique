// Externe libraries used: Arduino, TimerOne, ATOMIC
#include <Adafruit_PWMServoDriver.h>  // Servo object to control the servomotors
#include <Arduino.h>
#include <Bonezegei_A4988.h>  // Bonezegei_A4988 object to control the stepper motors
#include <Servo.h>            // Arduino framework

// Custom libraries used: Com
#include <com.h>  // Communication object to manage the communication between the teensy and the Raspberry Pi

// Configuration file (contains all the constants and pinout), it is just a
// main.cpp header file
#include <config.h>

// 1. Define the actuators tabs (pointers tab)
void* actuators[48] = {nullptr};
bool switch_pins[48] = {false};

// 2. Instanciate the Communication object
Com* com;

Adafruit_PWMServoDriver controller = Adafruit_PWMServoDriver(0x40);
// PCA9685 as 12 bits = 4096 ticks per complete cycle of PWM. 0°~500 μs and
// max~2500 μs generic, can be use but in reality depend of each servos, angles
// are not perfect as 180 not equal to 180 in real life but no time to fix
#define SERVOMIN 125
#define SERVOMAX 575

int angleToPulse(int angle, int max_angle) {
    int pulse = map(angle, 0, max_angle, SERVOMIN, SERVOMAX);
    return pulse;
}

void set_servo_angle(byte* msg, byte size) {
    msg_set_servo_angle* servo_set_angle_msg = (msg_set_servo_angle*)msg;
    String output = "pin:" + String(servo_set_angle_msg->pin);
    String output2 = "angle" + String(servo_set_angle_msg->angle);
    com->print((char*)output.c_str());
    com->print((char*)output2.c_str());
    if (actuators[servo_set_angle_msg->pin] == nullptr) {
        Servo* servo = new Servo();
        servo->attach(servo_set_angle_msg->pin);
        actuators[servo_set_angle_msg->pin] = (void*)servo;
    }
    Servo* servo = (Servo*)actuators[servo_set_angle_msg->pin];
    if (!servo->attached()) {
        servo->attach(servo_set_angle_msg->pin);
    }
    servo->write(servo_set_angle_msg->angle);
}

// 3. Define all com callback functions
// a. define the callback functions
void set_servo_angle_I2C(byte* msg, byte size) {
    msg_set_servo_angle_I2C* servo_set_angle_msg =
        (msg_set_servo_angle_I2C*)msg;
    String output = "pin:" + String(servo_set_angle_msg->pin);
    String output2 =
        "angle pulse:" + String(angleToPulse(servo_set_angle_msg->angle,
                                             servo_set_angle_msg->max_angle));
    com->print((char*)output.c_str());
    com->print((char*)output2.c_str());
    String output3 = "angle:" + String(servo_set_angle_msg->angle);
    com->print((char*)output3.c_str());
    controller.setPWM(servo_set_angle_msg->pin, 0,
                      angleToPulse(servo_set_angle_msg->angle,
                                   servo_set_angle_msg->max_angle));
}

void set_servo_angle_detach(
    byte* msg,
    byte size)  // TODO: Implement functional detach with i2c
{
    msg_set_servo_angle_detach* servo_angle_detach_msg =
        (msg_set_servo_angle_detach*)msg;
    if (actuators[servo_angle_detach_msg->pin] == nullptr) {
        Servo* servo = new Servo();
        servo->attach(servo_angle_detach_msg->pin);
        actuators[servo_angle_detach_msg->pin] = (void*)servo;
    }
    Servo* servo = (Servo*)actuators[servo_angle_detach_msg->pin];
    if (!servo->attached()) {
        servo->attach(servo_angle_detach_msg->pin);
    }
    servo->write(servo_angle_detach_msg->angle);
    delay(servo_angle_detach_msg->detach_delay);
    servo->detach();
}

void stepper_step(byte* msg, byte size) {
    msg_stepper_step* stepper_step_msg = (msg_stepper_step*)msg;
    if (actuators[stepper_step_msg->pin_dir] == nullptr) {
        Bonezegei_A4988* stepper = new Bonezegei_A4988(
            stepper_step_msg->pin_dir, stepper_step_msg->pin_step);
        stepper->begin();
        actuators[stepper_step_msg->pin_dir] = (void*)stepper;
        pinMode(stepper_step_msg->enable_pin_driver, OUTPUT);
    }
    String output1 = "pin dir:" + String(stepper_step_msg->pin_dir);
    String output2 = "pin step:" + String(stepper_step_msg->pin_step);
    String output3 = "speed:" + String(stepper_step_msg->speed);
    com->print((char*)output1.c_str());
    com->print((char*)output2.c_str());
    com->print((char*)output3.c_str());
    Bonezegei_A4988* stepper =
        (Bonezegei_A4988*)actuators[stepper_step_msg->pin_dir];
    stepper->setSpeed(stepper_step_msg->speed);

    // Step the motor
    digitalWrite(stepper_step_msg->enable_pin_driver, LOW);
    if (stepper_step_msg->dir)
        stepper->step(1, stepper_step_msg->steps);
    else
        stepper->step(0, stepper_step_msg->steps);
    // digitalWrite(stepper_step_msg->enable_pin_driver, HIGH);
    // TODO: Implement a way to disable the driver after the step is done, to
    // prevent heating
}

void set_stepper_driver_activation_state(byte* msg, byte size) {
    msg_set_stepper_driver_activation_state* stepper_driver_activation_msg =
        (msg_set_stepper_driver_activation_state*)msg;
    String output = "pin:" + String(stepper_driver_activation_msg->pin);
    String output2 = "enable driver state:" +
                     String(stepper_driver_activation_msg->enable_driver_state);
    com->print((char*)output.c_str());
    com->print((char*)output2.c_str());
    digitalWrite(stepper_driver_activation_msg->pin,
                 stepper_driver_activation_msg->enable_driver_state);
}

void attach_switch(byte* msg, byte size) {
    msg_attach_switch* attach_switch_msg = (msg_attach_switch*)msg;
    switch_pins[attach_switch_msg->pin] = true;
    // Define switch as input
    pinMode(attach_switch_msg->pin, INPUT);
    // Read the switch state
    actuators[attach_switch_msg->pin] =
        (void*)(digitalRead(attach_switch_msg->pin));

    // Send to the rasp the current state of the switch
    msg_switch_state_return switch_state_return_msg;
    switch_state_return_msg.pin = attach_switch_msg->pin;
    switch_state_return_msg.state = (bool)actuators[attach_switch_msg->pin];
    com->send_msg((byte*)&switch_state_return_msg,
                  sizeof(msg_switch_state_return));
}

// b. assign the callback functions to the right message id
void (*callback_functions[256])(byte* msg, byte size);

void initilize_callback_functions() {
    callback_functions[SET_SERVO_ANGLE_I2C] = &set_servo_angle_I2C;
    callback_functions[STEPPER_STEP] = &stepper_step;
    callback_functions[SET_SERVO_ANGLE_DETACH] = &set_servo_angle_detach;
    callback_functions[ATTACH_SWITCH] = &attach_switch;
    callback_functions[SET_SERVO_ANGLE] = &set_servo_angle;
    callback_functions[SET_STEPPER_DRIVER_ACTIVATION_STATE] =
        &set_stepper_driver_activation_state;
}
void setup() {
    pinMode(ENABLE_DRIVER_STEPPER_PIN,
            OUTPUT);  // Set the enable pin for the stepper driver as output
    digitalWrite(ENABLE_DRIVER_STEPPER_PIN,
                 HIGH);  // Immediatly set enable pin at high to prevent
                         // heating. Dirty solution.

    com = new Com(&Serial, BAUDRATE);
    controller.begin();
    controller.setPWMFreq(60);

    // Initialize callback functions
    initilize_callback_functions();
}

void loop() {
    com->handle_callback(callback_functions);

    // Check the switch state
    for (int i = 0; i < 48; i++) {
        if (switch_pins[i]) {
            bool state = digitalRead(i);
            if (state != (bool)actuators[i]) {
                actuators[i] = (void*)state;
                msg_switch_state_return switch_state_return_msg;
                switch_state_return_msg.pin = i;
                switch_state_return_msg.state = state;
                com->send_msg((byte*)&switch_state_return_msg,
                              sizeof(msg_switch_state_return));
            }
        }
    }
}
