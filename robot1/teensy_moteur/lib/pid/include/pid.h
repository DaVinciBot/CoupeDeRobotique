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
     * @param deadband Minimum output to overcome motor static friction (default 0)
     */
    PID(double kp, double ki, double kd,
        double minOutput = -255.0, double maxOutput = 255.0,
        double deadband = 0.0);

    /**
     * Updates the PID gain parameters and resets internal state.
     * @param kp New proportional gain
     * @param ki New integral gain
     * @param kd New derivative gain
     */
    void updateParameters(double kp, double ki, double kd);

    /**
     * Sets the PID gain parameters without altering internal state.
     */
    void setTunings(double kp, double ki, double kd);

    /**
     * Sets output limits.
     */
    void setOutputLimits(double minOutput, double maxOutput);

    /**
     * Sets the linear deadband around zero.
     * @param deadband absolute value of minimum output
     */
    void setDeadband(double deadband);

    /**
     * Computes the PID output based on the provided error.
     * Automatically updates the sample time based on micros().
     * @param error Difference between setpoint and measured value
     * @return Control output in range [minOutput, maxOutput]
     */
    double compute(double error);

    /**
     * Resets the integral and derivative state.
     */
    void reset();

private:
    void updateDeltaTime();
    double applyDeadband(double raw);

    double _kp;
    double _ki;
    double _kd;

    double _dt;
    double _minOutput;
    double _maxOutput;
    double _deadband;

    double _integral;
    double _previousError;
    unsigned long _lastTime;
};