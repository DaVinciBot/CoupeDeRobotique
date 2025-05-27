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
     */
    PID(double kp, double ki, double kd, double minOutput = -255.0, double maxOutput = 255.0);

    void setTunings(double kp, double ki, double kd);
    void setOutputLimits(double minOutput, double maxOutput);

    /**
     * Computes the PID output based on setpoint and current input.
     * Automatically updates the sample time based on micros().
     * @param error The difference between the setpoint and the current input.
     * @return Control output in range [minOutput, maxOutput]
     */
    double compute(double error);

    /**
     * Resets the integral and derivative state.
     */
    void reset();

private:
    void updateDeltaTime();

    double _kp;
    double _ki;
    double _kd;

    double _dt;
    double _minOutput;
    double _maxOutput;

    double _integral;
    double _previousError;
    unsigned long _lastTime;
};
