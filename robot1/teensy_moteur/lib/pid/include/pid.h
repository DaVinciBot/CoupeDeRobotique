/**
 * This is the PID class header
 * The PID class compute the error for the servo-control of the motors.
 */
#include <Arduino.h>

class PID {
public:
    /**
     * Constructs a PID controller.
     * @param kp Proportional gain
     * @param ki Integral gain
     * @param kd Derivative gain
     * @param minOutput Minimum output value (default -255.0)
     * @param maxOutput Maximum output value (default 255.0)
     * @param deadband Feed-forward friction threshold (default 0)
     */
    PID(double kp, double ki, double kd,
        double minOutput = -255.0, double maxOutput = 255.0,
        double deadband = 0.0);

    /**
     * Update PID gains and reset internal state.
     */
    void updateParameters(double kp, double ki, double kd);

    /**
     * Set PID gains (does not reset state).
     */
    void setTunings(double kp, double ki, double kd);

    /**
     * Set output limits.
     */
    void setOutputLimits(double minOutput, double maxOutput);

    /**
     * Set deadband threshold for feed-forward.
     */
    void setDeadband(double deadband);

    /**
     * Compute control output from error.
     * @param error Difference between setpoint and measurement.
     * @return Control signal in [minOutput, maxOutput].
     */
    double compute(double error);

    /**
     * Reset integral and derivative state.
     */
    void reset();

private:
    void updateDeltaTime();

    double _kp;
    double _ki;
    double _kd;

    double _minOutput;
    double _maxOutput;
    double _deadband;

    double _integral;
    double _previousError;
    double _dt;
    unsigned long _lastTime;

    // derivative filter state
    double _derivFiltered;
};