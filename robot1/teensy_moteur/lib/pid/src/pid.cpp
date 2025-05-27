/**
 * This is the implementation of the PID class.
 * The PID class compute the error for the servo-control of the motors.
 */

#include <pid.h>
#include <Arduino.h>

PID::PID(double kp, double ki, double kd,
         double minOutput, double maxOutput,
         double deadband)
    : _kp(kp)
    , _ki(ki)
    , _kd(kd)
    , _minOutput(minOutput)
    , _maxOutput(maxOutput)
    , _deadband(fabs(deadband))
    , _integral(0.0)
    , _previousError(0.0)
    , _dt(0.0)
    , _lastTime(micros())
    , _derivFiltered(0.0)
{
}

void PID::updateParameters(double kp, double ki, double kd) {
    setTunings(kp, ki, kd);
    reset();
}

void PID::setTunings(double kp, double ki, double kd) {
    _kp = kp;
    _ki = ki;
    _kd = kd;
}

void PID::setOutputLimits(double minOutput, double maxOutput) {
    if (minOutput >= maxOutput) return;
    _minOutput = minOutput;
    _maxOutput = maxOutput;
}

void PID::setDeadband(double deadband) {
    _deadband = fabs(deadband);
}

void PID::updateDeltaTime() {
    unsigned long now = micros();
    _dt = (now - _lastTime) * 1e-6;
    _lastTime = now;
}

double PID::compute(double error) {
    updateDeltaTime();

    // Derivative with one-pole low-pass filter
    double derivRaw = (_dt > 0.0) ? (error - _previousError) / _dt : 0.0;
    const double alpha = 0.8; // filter coefficient
    _derivFiltered = alpha * _derivFiltered + (1.0 - alpha) * derivRaw;

    // Proportional term
    double P = _kp * error;
    // Integral term (will update after anti-windup check)
    double I = _integral;
    // Derivative term
    double D = _kd * _derivFiltered;

    // Raw PID output
    double raw = P + I + D;

    // Feed-forward friction compensation
    double ff = 0.0;
    if (raw > 0.0) ff = _deadband;
    else if (raw < 0.0) ff = -_deadband;
    double u_pre = raw + ff;

    // Saturate
    double u_sat = constrain(u_pre, _minOutput, _maxOutput);

    // Anti-windup: integrate only if not saturated
    if (u_sat > _minOutput && u_sat < _maxOutput) {
        _integral += _ki * error * _dt;
        _integral = constrain(_integral, _minOutput, _maxOutput);
    }

    // Save error
    _previousError = error;
    return u_sat;
}

void PID::reset() {
    _integral = 0.0;
    _previousError = 0.0;
    _derivFiltered = 0.0;
    _lastTime = micros();
}
