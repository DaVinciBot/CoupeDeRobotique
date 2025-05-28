/**
 * This is the PID class header
 * The PID class compute the error for the servo-control of the motors.
 */
#include <Arduino.h>


/**
 * @brief Simple PID controller with deadband compensation.
 */
class PID {
public:
    /**
     * @param kp          Proportional gain
     * @param ki          Integral gain
     * @param kd          Derivative gain
     * @param minOutput   Minimum output (default -255)
     * @param maxOutput   Maximum output (default +255)
     * @param deadband    Friction compensation threshold (default 0)
     */
    PID(double kp, double ki, double kd,
        double minOutput = -255.0, double maxOutput = 255.0,
        double deadband = 0.0);

    /**
     * @brief Update PID gains and reset internal state.
     */
    void updateParameters(double kp, double ki, double kd);

    /**
     * @brief Set PID gains (without resetting state).
     */
    void setTunings(double kp, double ki, double kd);

    /**
     * @brief Set output limits.
     */
    void setOutputLimits(double minOutput, double maxOutput);

    /**
     * @brief Set deadband threshold for feedforward friction compensation.
     */
    void setDeadband(double deadband);

    /**
     * @brief Compute control signal from the error.
     * @param error  Setpoint - measurement
     * @return       PID output, clamped to [minOutput..maxOutput]
     */
    double compute(double error);

    /**
     * @brief Reset integral and derivative state.
     */
    void reset();

private:
    double _kp, _ki, _kd;
    double _minOutput, _maxOutput;
    double _deadband;

    double _integral;
    double _prevError;
    unsigned long _lastTime;
};