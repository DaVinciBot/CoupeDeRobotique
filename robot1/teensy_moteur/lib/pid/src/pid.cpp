/**
 * This is the implementation of the PID class.
 * The PID class compute the error for the servo-control of the motors.
 */

#include "PID.h"
#include <Arduino.h>

PID::PID(double kp,
         double ki,
         double kd,
         double minOutput,
         double maxOutput,
         double deadband,
         double dtMin,
         double dtMax)
    : _kp(kp),
      _ki(ki),
      _kd(kd),
      _minOutput(minOutput),
      _maxOutput(maxOutput),
      _deadband(fabs(deadband)),
      _integral(0.0),
      _prevError(0.0),
      _lastTime(micros()),
      _dtMin(dtMin),
      _dtMax(dtMax) {}

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
    // Clamp integral term to new limits (anti-windup)
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
    double dt = (now - _lastTime) * 1e-6;  // convert µs to s
    _lastTime = now;
    // Guard against too small or too large dt
    if (dt <= 0.0)
        dt = _dtMin;
    if (dt < _dtMin)
        dt = _dtMin;
    else if (dt > _dtMax)
        dt = _dtMax;

    // Integral update + clamp
    _integral += error * dt;
    if (_ki != 0.0) {
        double iMin = _minOutput / _ki;
        double iMax = _maxOutput / _ki;
        _integral = constrain(_integral, iMin, iMax);
    }

    // PID terms
    double pTerm = _kp * error;
    double iTerm = _ki * _integral;
    double dTerm = _kd * (error - _prevError) / dt;
    _prevError = error;

    // Combine
    double rawOutput = pTerm + iTerm + dTerm;

    // Apply smooth deadband
    double output = applyDeadband(rawOutput);

    // Final clamp to output limits
    return constrain(output, _minOutput, _maxOutput);
}

/**
 * @brief Smoothly remove the deadband around zero by linear mapping.
 * @param value  Raw controller output
 * @return Output with deadband removed
 */
double PID::applyDeadband(double value) {
    double mag = fabs(value);
    if (mag <= _deadband) {
        return 0.0;
    }
    double sign = (value > 0.0) ? 1.0 : -1.0;
    // Shift the magnitude down by deadband
    return sign * (mag - _deadband);
}
