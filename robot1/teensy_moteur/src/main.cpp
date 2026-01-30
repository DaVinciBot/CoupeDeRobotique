// Externe libraries used: Arduino, TimerOne, ATOMIC
#include <Arduino.h>      // Arduino framework
#include <TimerOne.h>     // Timer interrupt library
#include <stdio.h>        // snprintf
#include <util/atomic.h>  // Atomic block library

// Custom libraries used: RollingBasis, Com
#include <rolling_basis.h>  // Rolling Basis object to manage the motors and robot position

// Configuration file (contains all the constants and pinout), it is just a
// main.cpp header file
#include <config.h>

// 1. Instanciate the Rolling Basis object
// a. Define the PID controllers
PID linear_velocity_pid(KP_LINEAR_VELOCITY,
                        KI_LINEAR_VELOCITY,
                        KD_LINEAR_VELOCITY,
                        -240,
                        240,
                        5.0);
PID angular_velocity_pid(KP_ANGULAR_VELOCITY,
                         KI_ANGULAR_VELOCITY,
                         KD_ANGULAR_VELOCITY,
                         -200,
                         200,
                         0.001);

// b. Instanciate the Rolling Basis object
Rolling_Basis* rolling_basis_ptr = new Rolling_Basis(ENCODER_RESOLUTION,
                                                     ENTRAXE,
                                                     WHEEL_DIAMETER,
                                                     linear_velocity_pid,
                                                     angular_velocity_pid);

// 2. Instanciate the Communication object
Com* com;

// c. Define the motors interrupt functions
/******* Attach Interrupt *******/
inline void left_motor_read_encoder() {
    if (digitalRead(L_ENCB))
        rolling_basis_ptr->left_motor->ticks++;
    else
        rolling_basis_ptr->left_motor->ticks--;
}

inline void right_motor_read_encoder() {
    if (digitalRead(R_ENCB))
        rolling_basis_ptr->right_motor->ticks--;
    else
        rolling_basis_ptr->right_motor->ticks++;
}

// 3. Define all com callback functions
// a. define globals variables to keep in memory callback functions updated
VelocityCommand target_velocity;
volatile unsigned long last_command_us = 0;

// b. define the callback functions
void set_target_velocity(byte* msg, byte size) {
    msg_set_target_velocity* target_velocity_msg =
        (msg_set_target_velocity*)msg;

    unsigned long now = micros();

    // Update velocity target atomically (used by interrupt handler)
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        target_velocity.linear =
            target_velocity_msg->linear_velocity * M_S_TO_CM_S;
        target_velocity.angular = target_velocity_msg->angular_velocity;
        last_command_us = now;
    }
}

void set_pid(byte* msg, byte size) {
    msg_set_pid* pid_msg = (msg_set_pid*)msg;
    PID* pid = nullptr;
    bool is_valid_pid = true;
    switch (pid_msg->pid_type) {
        case LINEAR_VELOCITY_PID_ID:
            pid = &rolling_basis_ptr->linear_velocity_pid;
            break;
        case ANGULAR_VELOCITY_PID_ID:
            pid = &rolling_basis_ptr->angular_velocity_pid;
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

    unsigned long now = micros();
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        rolling_basis_ptr->X = odometrie->x;
        rolling_basis_ptr->Y = odometrie->y;
        rolling_basis_ptr->THETA = odometrie->theta;

        rolling_basis_ptr->linear_velocity = 0.0;
        rolling_basis_ptr->angular_velocity = 0.0;
        rolling_basis_ptr->last_odometrie_time = now;
        target_velocity = VelocityCommand();
    }
}

void reset_teensy(byte* msg, byte size) {
    volatile uint32_t* aircr = (volatile uint32_t*)0xE000ED0C;
    *aircr = 0x05FA0004;
}

// c. assign the callback functions to the right message id
void (*callback_functions[256])(byte* msg, byte size);

void initialize_callback_functions() {
    callback_functions[SET_TARGET_VELOCITY] = &set_target_velocity;
    callback_functions[SET_PID] = &set_pid;
    callback_functions[SET_ODOMETRIE] = &set_odometrie;
    callback_functions[RESET_TEENSY] = &reset_teensy;
}

// 4. Define the timer interrupt handle function (this function will be called
// every 10ms, and which manage the robot position and speed: asservissement)
void handle() {
    rolling_basis_ptr->odometrie_handle();
    unsigned long now = micros();
    VelocityCommand target;
    unsigned long last_cmd_us = 0;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        target = target_velocity;
        last_cmd_us = last_command_us;
    }
    if (last_cmd_us != 0 && now - last_cmd_us > COMMAND_TIMEOUT_US) {
        target = VelocityCommand();
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
            target_velocity = target;
        }
    }
    rolling_basis_ptr->handle(target);
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

    static uint32_t last_pwm_log_ms = 0;
    uint32_t now_ms = millis();
    if (now_ms - last_pwm_log_ms >= 200) {
        int16_t right_pwm = 0;
        int16_t left_pwm = 0;
        long right_ticks = 0;
        long left_ticks = 0;
        double target_lin = 0.0;
        double target_ang = 0.0;
        double v_lin = 0.0;
        double v_ang = 0.0;
        double err_lin = 0.0;
        double err_ang = 0.0;
        double corr_lin = 0.0;
        double corr_ang = 0.0;
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
            right_pwm = rolling_basis_ptr->right_motor->last_pwm;
            left_pwm = rolling_basis_ptr->left_motor->last_pwm;
            right_ticks = rolling_basis_ptr->right_motor->ticks;
            left_ticks = rolling_basis_ptr->left_motor->ticks;
            target_lin = target_velocity.linear;
            target_ang = target_velocity.angular;
            v_lin = rolling_basis_ptr->linear_velocity;
            v_ang = rolling_basis_ptr->angular_velocity;
            err_lin = rolling_basis_ptr->last_linear_error;
            err_ang = rolling_basis_ptr->last_angular_error;
            corr_lin = rolling_basis_ptr->last_linear_correction;
            corr_ang = rolling_basis_ptr->last_angular_correction;
        }
        int16_t tv_lin = static_cast<int16_t>(target_lin * 100);
        int16_t tv_ang = static_cast<int16_t>(target_ang * 100);
        int16_t mv_lin = static_cast<int16_t>(v_lin * 100);
        int16_t mv_ang = static_cast<int16_t>(v_ang * 100);
        int16_t ev_lin = static_cast<int16_t>(err_lin * 100);
        int16_t ev_ang = static_cast<int16_t>(err_ang * 100);
        int16_t cv_lin = static_cast<int16_t>(corr_lin);
        int16_t cv_ang = static_cast<int16_t>(corr_ang);

        char msg[96];
        snprintf(msg, sizeof(msg),
                 "RB tv=%d/%d v=%d/%d e=%d/%d c=%d/%d pwm=%d/%d ticks=%ld/%ld",
                 tv_lin, tv_ang, mv_lin, mv_ang, ev_lin, ev_ang, cv_lin, cv_ang,
                 left_pwm, right_pwm, left_ticks, right_ticks);
        com->print(msg);
        last_pwm_log_ms = now_ms;
    }

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
