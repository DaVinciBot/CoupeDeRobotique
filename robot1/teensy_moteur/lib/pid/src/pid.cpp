/**
 * This is the implementation of the PID class.
 * The PID class compute the error for the servo-control of the motors.
 */

#include <pid.h>
#include <Arduino.h>

/**
 * @brief Constructor for the PID class
 *
 * Initializes the 3 PID constant
 * @param kp Proportionnal constant
 * @param ki Integral constant
 * @param kd Derivative constant
 */
PID::PID(float kp, float ki, float kd)
{
    this->kp = kp;
    this->kd = kd;
    this->ki = ki;
}

/**
 * @brief Compute the time elapsed since the last time this method has been called.A0
 *
 * @return Time elapsed
 */
double PID::delta_time_calculator()
{
    long current_time = micros();
    double delta_time = (current_time - this->prevT) / (1e6); // convert to in seconds
    this->prevT = current_time;
    return delta_time;
}

/**
 * @brief Compute error.
 *
 * @param error Previous error computed
 * @return New error
 */
float PID::compute(float error)
{
    // double delta_time = this->delta_time_calculator();

    // Calculate derivative
    float derivative = error - this->error_prev;

    // Calculate integral
    this->error_integral += error;

    // Control signal
    float new_error = this->kp * error - this->kd * derivative + this->ki * this->error_integral;

    // Save error
    this->error_prev = error;

    return new_error;
}