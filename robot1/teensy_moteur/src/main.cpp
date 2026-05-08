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
PID linear_position_pid(KP_LINEAR_POSITION,
                        KI_LINEAR_POSITION,
                        KD_LINEAR_POSITION,
                        -POSITION_MAX_LINEAR_STEP_CM,
                        POSITION_MAX_LINEAR_STEP_CM,
                        POSITION_LINEAR_DEADBAND);
PID angular_position_pid(KP_ANGULAR_POSITION,
                         KI_ANGULAR_POSITION,
                         KD_ANGULAR_POSITION,
                         -POSITION_MAX_ANGULAR_STEP_CM,
                         POSITION_MAX_ANGULAR_STEP_CM,
                         POSITION_ANGULAR_DEADBAND);
PID left_wheel_position_pid(KP_LEFT_WHEEL_POSITION,
                            KI_LEFT_WHEEL_POSITION,
                            KD_LEFT_WHEEL_POSITION,
                            -WHEEL_POSITION_MAX_PWM,
                            WHEEL_POSITION_MAX_PWM,
                            WHEEL_POSITION_DEADBAND_CM);
PID right_wheel_position_pid(KP_RIGHT_WHEEL_POSITION,
                             KI_RIGHT_WHEEL_POSITION,
                             KD_RIGHT_WHEEL_POSITION,
                             -WHEEL_POSITION_MAX_PWM,
                             WHEEL_POSITION_MAX_PWM,
                             WHEEL_POSITION_DEADBAND_CM);

// b. Instanciate the Rolling Basis object
Rolling_Basis* rolling_basis_ptr = new Rolling_Basis(ENCODER_RESOLUTION,
                                                     ENTRAXE,
                                                     LEFT_WHEEL_DIAMETER,
                                                     RIGHT_WHEEL_DIAMETER,
                                                     linear_position_pid,
                                                     angular_position_pid,
                                                     left_wheel_position_pid,
                                                     right_wheel_position_pid);

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
        rolling_basis_ptr->right_motor->ticks++;
    else
        rolling_basis_ptr->right_motor->ticks--;
}

// 3. Define all com callback functions
// b. define the callback functions
void set_pid(byte* msg, byte size) {
    msg_set_pid* pid_msg = (msg_set_pid*)msg;
    PID* pid = nullptr;
    bool is_valid_pid = true;
    switch (pid_msg->pid_type) {
        case LINEAR_POSITION_PID_ID:
            pid = &rolling_basis_ptr->linear_position_pid;
            break;
        case ANGULAR_POSITION_PID_ID:
            pid = &rolling_basis_ptr->angular_position_pid;
            break;
        case LEFT_WHEEL_POSITION_PID_ID:
            pid = &rolling_basis_ptr->left_wheel_position_pid;
            break;
        case RIGHT_WHEEL_POSITION_PID_ID:
            pid = &rolling_basis_ptr->right_wheel_position_pid;
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

        rolling_basis_ptr->last_odometrie_time = now;
        rolling_basis_ptr->last_linear_error = 0.0;
        rolling_basis_ptr->last_angular_error = 0.0;
        rolling_basis_ptr->last_linear_correction = 0.0;
        rolling_basis_ptr->last_angular_correction = 0.0;
        rolling_basis_ptr->last_left_wheel_error = 0.0;
        rolling_basis_ptr->last_right_wheel_error = 0.0;
        rolling_basis_ptr->left_wheel_target_cm = 0.0;
        rolling_basis_ptr->right_wheel_target_cm = 0.0;
        rolling_basis_ptr->target_position =
            Point(odometrie->x, odometrie->y, odometrie->theta);
        rolling_basis_ptr->right_motor->ticks = 0L;
        rolling_basis_ptr->right_motor->last_ticks = 0L;
        rolling_basis_ptr->right_motor->last_delta_ticks = 0L;
        rolling_basis_ptr->right_motor->distance = 0.0;
        rolling_basis_ptr->left_motor->ticks = 0L;
        rolling_basis_ptr->left_motor->last_ticks = 0L;
        rolling_basis_ptr->left_motor->last_delta_ticks = 0L;
        rolling_basis_ptr->left_motor->distance = 0.0;
        rolling_basis_ptr->linear_position_pid.reset();
        rolling_basis_ptr->angular_position_pid.reset();
        rolling_basis_ptr->left_wheel_position_pid.reset();
        rolling_basis_ptr->right_wheel_position_pid.reset();
    }
}

void set_target_position(byte* msg, byte size) {
    msg_set_target_position* position_msg = (msg_set_target_position*)msg;
    Point position(position_msg->target_position_x,
                   position_msg->target_position_y,
                   position_msg->target_position_theta);
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        rolling_basis_ptr->set_target_position(position);
    }
}

void set_motors_pwm(byte* msg, byte size) {
    msg_set_motors_pwm* pwm_msg = (msg_set_motors_pwm*)msg;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        rolling_basis_ptr->set_motors_pwm(pwm_msg->left_pwm, pwm_msg->right_pwm,
                                          pwm_msg->duration_ms);
    }
}

void reset_teensy(byte* msg, byte size) {
    volatile uint32_t* aircr = (volatile uint32_t*)0xE000ED0C;
    *aircr = 0x05FA0004;
}

// c. assign the callback functions to the right message id
void (*callback_functions[256])(byte* msg, byte size);

void initialize_callback_functions() {
    callback_functions[SET_PID] = &set_pid;
    callback_functions[SET_ODOMETRIE] = &set_odometrie;
    callback_functions[RESET_TEENSY] = &reset_teensy;
    callback_functions[SET_TARGET_POSITION] = &set_target_position;
    callback_functions[SET_MOTORS_PWM] = &set_motors_pwm;
}

// 4. Define the timer interrupt handle function.
void handle() {
    rolling_basis_ptr->odometrie_handle();
    rolling_basis_ptr->handle();
}

void setup() {
    com = new Com(&Serial, BAUDRATE);

    // Change pwm frequency
    analogWriteFrequency(R_PWM, PWM_FREQUENCY);
    analogWriteFrequency(L_PWM, PWM_FREQUENCY);

    // Init Rolling Basis
    rolling_basis_ptr->define_right_motor(R_ENCA, R_ENCB, R_PWM, R_IN1, R_IN2,
                                          MAX_PWM, R_MIN_MOVING_PWM,
                                          MOTOR_PWM_SLEW_PER_CYCLE);
    rolling_basis_ptr->define_left_motor(L_ENCA, L_ENCB, L_PWM, L_IN1, L_IN2,
                                         MAX_PWM, L_MIN_MOVING_PWM,
                                         MOTOR_PWM_SLEW_PER_CYCLE);
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
        double err_lin = 0.0;
        double err_ang = 0.0;
        double corr_lin = 0.0;
        double corr_ang = 0.0;
        double left_wheel_error = 0.0;
        double right_wheel_error = 0.0;
        long right_delta_ticks = 0;
        long left_delta_ticks = 0;
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
            right_pwm = rolling_basis_ptr->right_motor->last_pwm;
            left_pwm = rolling_basis_ptr->left_motor->last_pwm;
            right_ticks = rolling_basis_ptr->right_motor->ticks;
            left_ticks = rolling_basis_ptr->left_motor->ticks;
            right_delta_ticks =
                rolling_basis_ptr->right_motor->last_delta_ticks;
            left_delta_ticks = rolling_basis_ptr->left_motor->last_delta_ticks;
            err_lin = rolling_basis_ptr->last_linear_error;
            err_ang = rolling_basis_ptr->last_angular_error;
            corr_lin = rolling_basis_ptr->last_linear_correction;
            corr_ang = rolling_basis_ptr->last_angular_correction;
            left_wheel_error = rolling_basis_ptr->last_left_wheel_error;
            right_wheel_error = rolling_basis_ptr->last_right_wheel_error;
        }
        long ev_lin = static_cast<long>(err_lin * 100.0);
        long ev_ang = static_cast<long>(err_ang * 100.0);
        long cv_lin = static_cast<long>(corr_lin * 100.0);
        long cv_ang = static_cast<long>(corr_ang * 100.0);
        long ew_left = static_cast<long>(left_wheel_error * 100.0);
        long ew_right = static_cast<long>(right_wheel_error * 100.0);

        char msg[160];
        snprintf(msg, sizeof(msg),
                 "RB e=%ld/%ld step=%ld/%ld ew=%ld/%ld pwm=%d/%d dt=%ld/%ld "
                 "ticks=%ld/%ld",
                 ev_lin, ev_ang, cv_lin, cv_ang, ew_left, ew_right, left_pwm,
                 right_pwm, left_delta_ticks, right_delta_ticks, left_ticks,
                 right_ticks);
        com->print(msg);
        last_pwm_log_ms = now_ms;
    }

    // Send rolling basis state
    if (counter++ > 4096)  // 4096 = 2^12
    {
        msg_update_rolling_basis rolling_basis_msg;
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
            rolling_basis_msg.x = rolling_basis_ptr->X;
            rolling_basis_msg.y = rolling_basis_ptr->Y;
            rolling_basis_msg.theta = rolling_basis_ptr->THETA;
            rolling_basis_msg.target_x = rolling_basis_ptr->target_position.x;
            rolling_basis_msg.target_y = rolling_basis_ptr->target_position.y;
            rolling_basis_msg.target_theta =
                rolling_basis_ptr->target_position.theta;
            rolling_basis_msg.linear_error =
                rolling_basis_ptr->last_linear_error;
            rolling_basis_msg.angular_error =
                rolling_basis_ptr->last_angular_error;
            rolling_basis_msg.linear_output =
                rolling_basis_ptr->last_linear_correction;
            rolling_basis_msg.angular_output =
                rolling_basis_ptr->last_angular_correction;
            rolling_basis_msg.left_wheel_target_cm =
                rolling_basis_ptr->left_wheel_target_cm;
            rolling_basis_msg.right_wheel_target_cm =
                rolling_basis_ptr->right_wheel_target_cm;
            rolling_basis_msg.left_wheel_position_cm =
                static_cast<double>(rolling_basis_ptr->left_motor->ticks) *
                rolling_basis_ptr->left_wheel_unit_tick_cm();
            rolling_basis_msg.right_wheel_position_cm =
                static_cast<double>(rolling_basis_ptr->right_motor->ticks) *
                rolling_basis_ptr->right_wheel_unit_tick_cm();
            rolling_basis_msg.left_wheel_error_cm =
                rolling_basis_ptr->last_left_wheel_error;
            rolling_basis_msg.right_wheel_error_cm =
                rolling_basis_ptr->last_right_wheel_error;
            rolling_basis_msg.left_pwm =
                rolling_basis_ptr->left_motor->last_pwm;
            rolling_basis_msg.right_pwm =
                rolling_basis_ptr->right_motor->last_pwm;
            rolling_basis_msg.left_ticks = rolling_basis_ptr->left_motor->ticks;
            rolling_basis_msg.right_ticks =
                rolling_basis_ptr->right_motor->ticks;
            rolling_basis_msg.left_delta_ticks =
                rolling_basis_ptr->left_motor->last_delta_ticks;
            rolling_basis_msg.right_delta_ticks =
                rolling_basis_ptr->right_motor->last_delta_ticks;
        }

        com->send_msg((byte*)&rolling_basis_msg,
                      sizeof(msg_update_rolling_basis));
        counter = 0;
    }
}
