/**
 * This is the implementation of the Motor class.
 * The Motor class control a Mmotor power and direction and handle odometry
 * computation.
 */

#include <Arduino.h>
#include <motors_driver.h>
#include <cmath>

#define ENCODER_PPR 1024
#define MOTOR_VEL_ALPHA 0.25
#define MOTOR_VEL_MIN_TICKS 3
#define MOTOR_NO_TICK_TIMEOUT_US 80000
#define MAX_RPM_AMT10 7500.0

/**
 * @brief Constructor of the Motor class
 * Define the pins of the motor, the related encoder pins and the properties of
 * the wheel attached to the motor
 */
Motor::Motor(byte pin_forward,
             byte pin_backward,
             byte pin_pwm,
             byte pin_enca,
             byte pin_encb,
             double wheel_unit_tick_cm,
             byte max_pwm) {
    this->pin_forward = pin_forward;
    this->pin_backward = pin_backward;

    this->pin_pwm = pin_pwm;    // PWM pin only !
    this->pin_enca = pin_enca;  // AttachInterrupt pin only !
    this->pin_encb = pin_encb;  // AttachInterrupt pin only !

    this->max_pwm = max_pwm;

    this->wheel_unit_tick_cm = wheel_unit_tick_cm;

    this->ticks = 0;
    this->last_ticks = 0;
    this->velocity_cm_s = 0.0;
    this->filtered_velocity_cm_s = 0.0;
    this->last_tick_time_us = 0;
    this->last_odometrie_time_us = micros();
}

/**
 * @brief Initialize the mode of the pins define for the motor
 */
void Motor::init() {
    pinMode(this->pin_forward, OUTPUT);
    pinMode(this->pin_backward, OUTPUT);
    pinMode(this->pin_pwm, OUTPUT);

    pinMode(this->pin_enca, INPUT);
    pinMode(this->pin_encb, INPUT);
}

/**
 * @brief Set motor PWM and direction
 *
 * @param pwmVal Power value of the motor
 */
void Motor::set_motor(int pwmVal) {
    int16_t dir = pwmVal > 0 ? 1 : -1;
    int16_t sign = (pwmVal > 0) ? 1 : (pwmVal < 0 ? -1 : 0);
    pwmVal = constrain(abs(pwmVal), 0, this->max_pwm);
    this->last_pwm = static_cast<int16_t>(sign * pwmVal);
    analogWrite(this->pin_pwm, pwmVal);
    if (dir == 1) {
        digitalWrite(this->pin_forward, HIGH);
        digitalWrite(this->pin_backward, LOW);
    } else if (dir == -1) {
        digitalWrite(this->pin_forward, LOW);
        digitalWrite(this->pin_backward, HIGH);
    } else {
        digitalWrite(this->pin_forward, LOW);
        digitalWrite(this->pin_backward, LOW);
    }
}

/**
 * @brief Compute odometry.
 * Compute distance travelled by the encoders wheel and the speed of the
 * encoders wheel.
 */
void Motor::handle_odometrie() {
    // Update Ticks
    long delta_ticks = this->ticks - this->last_ticks;
    this->last_ticks = this->ticks;

    // Compute new distance travelled
    this->distance = delta_ticks * this->wheel_unit_tick_cm;

    unsigned long now = micros();
    double dt = 0.0;
    if (this->last_odometrie_time_us != 0UL) {
        dt = (now - this->last_odometrie_time_us) * 1e-6;
    }
    this->last_odometrie_time_us = now;

    double raw_velocity = 0.0;
    bool has_sample = false;

    long abs_ticks = (delta_ticks >= 0) ? delta_ticks : -delta_ticks;
    if (abs_ticks >= MOTOR_VEL_MIN_TICKS && dt > 0.0) {
        raw_velocity = (delta_ticks * this->wheel_unit_tick_cm) / dt;
        has_sample = true;
        this->last_tick_time_us = now;
    } else if (delta_ticks != 0) {
        if (this->last_tick_time_us != 0UL) {
            double dt_tick = (now - this->last_tick_time_us) * 1e-6;
            if (dt_tick > 0.0) {
                double sign = (delta_ticks > 0) ? 1.0 : -1.0;
                raw_velocity = sign * this->wheel_unit_tick_cm / dt_tick;
                has_sample = true;
            }
        }
        this->last_tick_time_us = now;
    } else if (this->last_tick_time_us != 0UL &&
               (now - this->last_tick_time_us) > MOTOR_NO_TICK_TIMEOUT_US) {
        raw_velocity = 0.0;
        has_sample = true;
    }

    if (has_sample) {
        double wheel_perimeter = this->wheel_unit_tick_cm * ENCODER_PPR;
        double max_velocity = (MAX_RPM_AMT10 * wheel_perimeter) / 60.0;
        if (fabs(raw_velocity) <= 1.2 * max_velocity) {
            this->velocity_cm_s = raw_velocity;
            this->filtered_velocity_cm_s +=
                MOTOR_VEL_ALPHA * (raw_velocity - this->filtered_velocity_cm_s);
        }
    }
}
