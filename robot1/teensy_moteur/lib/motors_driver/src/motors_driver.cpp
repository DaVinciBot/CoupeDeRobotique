/**
 * This is the implementation of the Motor class.
 * The Motor class control a Mmotor power and direction and handle odometry
 * computation.
 */

#include <Arduino.h>
#include <motors_driver.h>

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
             byte max_pwm,
             byte min_moving_pwm,
             byte pwm_slew_per_cycle) {
    this->pin_forward = pin_forward;
    this->pin_backward = pin_backward;

    this->pin_pwm = pin_pwm;    // PWM pin only !
    this->pin_enca = pin_enca;  // AttachInterrupt pin only !
    this->pin_encb = pin_encb;  // AttachInterrupt pin only !

    this->max_pwm = max_pwm;
    this->min_moving_pwm = constrain(min_moving_pwm, 0, max_pwm);
    this->pwm_slew_per_cycle = pwm_slew_per_cycle;

    this->wheel_unit_tick_cm = wheel_unit_tick_cm;

    this->ticks = 0;
    this->last_ticks = 0;
    this->last_delta_ticks = 0;
    this->current_pwm = 0;
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
    int16_t target_pwm = 0;
    if (pwmVal != 0) {
        int16_t sign = (pwmVal > 0) ? 1 : -1;
        int16_t logical_pwm = constrain(abs(pwmVal), 1, this->max_pwm);
        int16_t physical_pwm =
            map(logical_pwm, 1, this->max_pwm, this->min_moving_pwm,
                this->max_pwm);
        target_pwm = static_cast<int16_t>(sign * physical_pwm);
    }

    if (target_pwm == 0 || this->pwm_slew_per_cycle == 0) {
        this->current_pwm = target_pwm;
    } else if (target_pwm > this->current_pwm) {
        this->current_pwm =
            min(static_cast<int16_t>(this->current_pwm +
                                     this->pwm_slew_per_cycle),
                target_pwm);
    } else if (target_pwm < this->current_pwm) {
        this->current_pwm =
            max(static_cast<int16_t>(this->current_pwm -
                                     this->pwm_slew_per_cycle),
                target_pwm);
    }

    int16_t dir = (this->current_pwm > 0)
                      ? 1
                      : (this->current_pwm < 0 ? -1 : 0);
    pwmVal = constrain(abs(this->current_pwm), 0, this->max_pwm);
    this->last_pwm = this->current_pwm;
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

void Motor::set_motor_raw(int pwmVal) {
    int16_t dir = (pwmVal > 0) ? 1 : (pwmVal < 0 ? -1 : 0);
    int16_t sign = (pwmVal > 0) ? 1 : (pwmVal < 0 ? -1 : 0);
    pwmVal = constrain(abs(pwmVal), 0, this->max_pwm);
    this->current_pwm = static_cast<int16_t>(sign * pwmVal);
    this->last_pwm = this->current_pwm;
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
 * Compute distance travelled by the encoder wheel.
 */
void Motor::handle_odometrie() {
    // Update Ticks
    long delta_ticks = this->ticks - this->last_ticks;
    this->last_delta_ticks = delta_ticks;
    this->last_ticks = this->ticks;

    // Compute new distance travelled
    this->distance = delta_ticks * this->wheel_unit_tick_cm;
}
