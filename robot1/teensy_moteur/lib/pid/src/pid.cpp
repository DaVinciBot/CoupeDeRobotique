/**
 * This is the implementation of the PID class.
 * The PID class compute the error for the servo-control of the motors.
 */

#include <Arduino.h>
#include <pid.h>

PID::PID(double kp,
         double ki,
         double kd,
         double minOutput,
         double maxOutput,
         double deadband)
    : _kp(kp),
      _ki(ki),
      _kd(kd),
      _minOutput(minOutput),
      _maxOutput(maxOutput),
      _deadband(fabs(deadband)),
      _integral(0.0),
      _prevError(0.0),
      _lastTime(micros()) {}

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
    if (minOutput >= maxOutput)
        return;
    _minOutput = minOutput;
    _maxOutput = maxOutput;
    // Clamp accumulated integral to new limits
    if (_ki != 0.0) {
        double iMin = _minOutput / _ki;
        double iMax = _maxOutput / _ki;
        _integral = constrain(_integral, iMin, iMax);
    }
}

void PID::setDeadband(double deadband) {
    _deadband = fabs(deadband);
}

void PID::reset() {
    _integral = 0.0;
    _prevError = 0.0;
    _lastTime = micros();
}

double PID::compute(double error) {
    unsigned long now = micros();
    double dt = (now - _lastTime) * 1e-6;  // seconds
    _lastTime = now;
    if (dt <= 0.0)
        dt = 1e-6;
    // Prevent excessively small dt (spikes in derivative)
    const double dtMin = 1e-3;
    if (dt < dtMin)
        dt = dtMin;

    // 1) Integral update + clamp (anti-windup)
    _integral += error * dt;
    if (_ki != 0.0) {
        double iMin = _minOutput / _ki;
        double iMax = _maxOutput / _ki;
        _integral = constrain(_integral, iMin, iMax);
    }

    // 2) PID terms
    double pTerm = _kp * error;
    double iTerm = _ki * _integral;
    double dTerm = _kd * (error - _prevError) / dt;
    _prevError = error;

    double output = pTerm + iTerm + dTerm;

    // 3) Deadband kick for static friction
    if (output > 0.0)
        output += _deadband;
    else if (output < 0.0)
        output -= _deadband;

    // 4) Final clamp
    return constrain(output, _minOutput, _maxOutput);
}
