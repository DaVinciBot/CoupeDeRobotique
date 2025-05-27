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
     * @param deadband Threshold below which small outputs are boosted linearly
     */
    PID(double kp, double ki, double kd,
        double minOutput = -255.0, double maxOutput = 255.0,
        double deadband = 0.0);

    void updateParameters(double kp, double ki, double kd);
    void setTunings(double kp, double ki, double kd);
    void setOutputLimits(double minOutput, double maxOutput);
    void setDeadband(double deadband);
    double compute(double error);
    void reset();

private:
    void updateDeltaTime();
    double applyDeadbandBoost(double raw);

    double _kp;
    double _ki;
    double _kd;

    double _dt;
    double _minOutput;
    double _maxOutput;
    double _deadband;
    double _boostFactor;

    double _integral;
    double _previousError;
    unsigned long _lastTime;
};