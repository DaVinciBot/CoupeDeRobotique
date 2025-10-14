#ifndef PID_H
#define PID_H

#include <Arduino.h>

/**
 * @brief PID controller for servo-controlled motors with smooth deadband and dt
 * limits.
 *
 * Provides proportional, integral, and derivative control with:
 * - Anti-windup via integral clamping
 * - Variable dt handling with minimum and maximum thresholds
 * - Smooth deadband removal around zero to handle static friction
 */
class PID {
   public:
    /**
     * @param kp            Proportional gain
     * @param ki            Integral gain
     * @param kd            Derivative gain
     * @param minOutput     Minimum output value
     * @param maxOutput     Maximum output value
     * @param deadband      Deadband width around zero (units of output)
     * @param dtMin         Minimum dt (s) for derivative computation (default
     * 1e-3)
     * @param dtMax         Maximum dt (s) for integral/derivative (default
     * 0.02)
     */
    PID(double kp,
        double ki,
        double kd,
        double minOutput,
        double maxOutput,
        double deadband,
        double dtMin = 1e-3,
        double dtMax = 0.02);

    /**
     * @brief Update PID gains and reset internal state.
     */
    void updateParameters(double kp, double ki, double kd);

    /**
     * @brief Set PID tunings without resetting state.
     */
    void setTunings(double kp, double ki, double kd);

    /**
     * @brief Set output limits and clamp integral term for anti-windup.
     */
    void setOutputLimits(double minOutput, double maxOutput);

    /**
     * @brief Set deadband width (converted to positive).
     */
    void setDeadband(double deadband);

    /**
     * @brief Compute the PID output for given error.
     * @param error  Current error (setpoint - measurement)
     * @return PID output clamped to [minOutput, maxOutput]
     */
    double compute(double error);

    /**
     * @brief Reset internal integral and derivative history.
     */
    void reset();

   private:
    double _kp, _ki, _kd;
    double _minOutput, _maxOutput;
    double _deadband;
    double _integral;
    double _prevError;
    unsigned long _lastTime;
    double _dtMin, _dtMax;

    /**
     * @brief Remove deadband around zero with smooth linear mapping.
     */
    double applyDeadband(double value);
};

#endif  // PID_H
