/**
 * This is the PID class header
 * The PID class compute the error for the servo-control of the motors.
 */
#include <Arduino.h>
class PID
{
private:
    double error_prev = 0.0;     // Previous error saved for the next computation of the error
    double error_integral = 0.0; // Integral error that need to be updated each time the error is computed

public:
    // PID constants
    float kp;
    float ki;
    float kd;

    // Delta Time saver
    long prevT = 0L;

    /**
     * @brief Compute the time elapsed since the last time this method has been called.A0
     *
     * @return Time elapsed
     */
    double delta_time_calculator();

    /**
     * @brief Constructor for the PID class
     *
     * Initializes the 3 PID constant
     * @param kp Proportionnal constant
     * @param ki Integral constant
     * @param kd Derivative constant
     */
    PID(float kp, float ki, float kd);

    /**
     * @brief Compute error.
     *
     * @param error Previous error computed
     * @return New error
     */
    double compute(double error);

    double compute_derived_output_control(float error, float output);
};