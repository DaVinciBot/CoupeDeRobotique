// Externe libraries used: Arduino, TimerOne, ATOMIC
#include <Arduino.h>      // Arduino framework
#include <TimerOne.h>     // Timer interrupt library
#include <util/atomic.h>  // Atomic block library

// Custom libraries used: RollingBasis, Com
#include <rolling_basis.h>  // Rolling Basis object to manage the motors and robot position

// Configuration file (contains all the constants and pinout), it is just a
// main.cpp header file
#include <config.h>

// 1. Instanciate the Rolling Basis object
// a. Define the PID controllers
PID linear_distance_pid(KP_LINEAR_DISTANCE,
                        KI_LINEAR_DISTANCE,
                        KD_LINEAR_DISTANCE,
                        -240,
                        240,
                        5.0);
PID angular_distance_pid(KP_ANGULAR_DISTANCE,
                         KI_ANGULAR_DISTANCE,
                         KD_ANGULAR_DISTANCE,
                         -200,
                         200,
                         2.0);

// b. Instanciate the Rolling Basis object
Rolling_Basis* rolling_basis_ptr = new Rolling_Basis(ENCODER_RESOLUTION,
                                                     ENTRAXE,
                                                     WHEEL_DIAMETER,
                                                     linear_distance_pid,
                                                     angular_distance_pid);

// 2. Instanciate the Communication object
Com* com;

// c. Define the motors interrupt functions
/******* Attach Interrupt *******/
inline void left_motor_read_encoder() {
    if (digitalRead(L_ENCB))
        rolling_basis_ptr->left_motor->ticks--;
    else
        rolling_basis_ptr->left_motor->ticks++;
}

inline void right_motor_read_encoder() {
    if (digitalRead(R_ENCB))
        rolling_basis_ptr->right_motor->ticks--;
    else
        rolling_basis_ptr->right_motor->ticks++;
}

// 3. Define all com callback functions
// a. define globals variables to keep in memory callback functions updated
Point target_position(START_X, START_Y, START_THETA);

// b. define the callback functions
void set_target_position(byte* msg, byte size) {
    msg_set_target_position* target_position_msg =
        (msg_set_target_position*)msg;

    // Update position
    target_position.x = target_position_msg->target_position_x;
    target_position.y = target_position_msg->target_position_y;
    target_position.theta = target_position_msg->target_position_theta;
}

void set_pid(byte* msg, byte size) {
    msg_set_pid* pid_msg = (msg_set_pid*)msg;
    PID* pid = nullptr;
    bool is_valid_pid = true;
    switch (pid_msg->pid_type) {
        case LINEAR_POSITION_PID_ID:
            pid = &rolling_basis_ptr->linear_distance_pid;
            break;
        case ANGULAR_POSITION_PID_ID:
            pid = &rolling_basis_ptr->angular_distance_pid;
            break;
        default:
            is_valid_pid = false;
            break;
    }
    if (is_valid_pid) {
        pid->updateParameters(pid_msg->kp, pid_msg->ki, pid_msg->kd);
    }
}

void set_odometrie(byte* msg, byte size) {
    msg_set_odometrie* odometrie = (msg_set_odometrie*)msg;

    rolling_basis_ptr->X = odometrie->x;
    rolling_basis_ptr->Y = odometrie->y;
    rolling_basis_ptr->THETA = odometrie->theta;

    // Update target position: avoid the usage of old stored target point
    target_position.x = odometrie->x;
    target_position.y = odometrie->y;
    target_position.theta = odometrie->theta;
}

void reset_teensy(byte* msg, byte size) {
    // TODO: reset the teensy, à tester !
    void (*reboot)(void) = 0;
    reboot();
}

// c. assign the callback functions to the right message id
void (*callback_functions[256])(byte* msg, byte size);

void initialize_callback_functions() {
    callback_functions[SET_TARGET_POSITION] = &set_target_position;
    callback_functions[SET_PID] = &set_pid;
    callback_functions[SET_ODOMETRIE] = &set_odometrie;
    callback_functions[RESET_TEENSY] = &reset_teensy;
}

// 4. Define the timer interrupt handle function (this function will be called
// every 10ms, and which manage the robot position and speed: asservissement)
void handle() {
    rolling_basis_ptr->odometrie_handle();
    rolling_basis_ptr->handle(target_position, com);
}

void setup() {
    com = new Com(&Serial, BAUDRATE);

    // Change pwm frequency
    analogWriteFrequency(R_PWM, PWM_FREQUENCY);
    analogWriteFrequency(L_PWM, PWM_FREQUENCY);

    // Init Rolling Basis
    rolling_basis_ptr->define_right_motor(R_ENCA, R_ENCB, R_PWM, R_IN2, R_IN1,
                                          MAX_PWM);
    rolling_basis_ptr->define_left_motor(L_ENCA, L_ENCB, L_PWM, L_IN2, L_IN1,
                                         MAX_PWM);
    rolling_basis_ptr->init_motors();

    rolling_basis_ptr->init_rolling_basis(START_X, START_Y, START_THETA);
    attachInterrupt(digitalPinToInterrupt(L_ENCA), left_motor_read_encoder,
                    RISING);
    attachInterrupt(digitalPinToInterrupt(R_ENCA), right_motor_read_encoder,
                    RISING);

    // Init motors handle timer
    Timer1.initialize(ASSERVISSEMENT_FREQUENCY);
    Timer1.attachInterrupt(handle);

    // Initialize callback functions
    initialize_callback_functions();
}

uint_fast32_t counter = 0;
void loop() {
    // Handle the communication
    com->handle_callback(callback_functions);

    // Send rolling basis state
    if (counter++ > 4096)  // 4096 = 2^12
    {
        msg_update_rolling_basis rolling_basis_msg;
        // Rolling Basis position
        rolling_basis_msg.x = rolling_basis_ptr->X;
        rolling_basis_msg.y = rolling_basis_ptr->Y;
        rolling_basis_msg.theta = rolling_basis_ptr->THETA;

        com->send_msg((byte*)&rolling_basis_msg,
                      sizeof(msg_update_rolling_basis));
        counter = 0;
    }
}

/*

 This code was realized by Florian BARRE
    ____ __
   / __// /___
  / _/ / // _ \
 /_/  /_/ \___/

*/
