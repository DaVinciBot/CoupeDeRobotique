/**
 * This is the implementation of the PID class.
 * The PID class compute the error for the servo-control of the motors.
 */

#include <pid.h>
#include <Arduino.h>

PID::PID(double kp, double ki, double kd,
         double minOutput, double maxOutput,
         double deadband)
    : _kp(kp), _ki(ki), _kd(kd),
      _minOutput(minOutput), _maxOutput(maxOutput),
      _deadband(deadband),
      _integral(0.0), _previousError(0.0),
      _lastTime(micros()), _dt(0.0) {}

void PID::updateParameters(double kp, double ki, double kd) {
    this->setTunings(kp, ki, kd);
    this->reset();
}

void PID::setTunings(double kp, double ki, double kd) {
    this->_kp = kp;
    this->_ki = ki;
    this->_kd = kd;
}

void PID::setOutputLimits(double minOutput, double maxOutput) {
    if (minOutput >= maxOutput) return;
    this->_minOutput = minOutput;
    this->_maxOutput = maxOutput;
    if (this->_integral > this->_maxOutput) this->_integral = this->_maxOutput;
    else if (this->_integral < this->_minOutput) this->_integral = this->_minOutput;
}

void PID::setDeadband(double deadband) {
    this->_deadband = fabs(deadband);
}

void PID::updateDeltaTime() {
    unsigned long now = micros();
    this->_dt = (now - this->_lastTime) * 1e-6;
    this->_lastTime = now;
}

/**
 * Applies a linear deadband compensation: maps raw ∈ [0,maxOutput]
 * to [deadband, maxOutput] linearly. Zero remains zero.
 */

double PID::applyDeadband(double raw) {
    double sign = (raw >= 0) ? 1.0 : -1.0;
    double absRaw = fabs(raw);
    if (absRaw <= 0 || this->_deadband <= 0) {
        return raw;
    }
    double scaled = this->_deadband + absRaw * (this->_maxOutput - this->_deadband) / this->_maxOutput;
    if (scaled > this->_maxOutput) scaled = this->_maxOutput;
    return sign * scaled;
}

double PID::compute(double error) {
    this->updateDeltaTime();

    // Integral term
    this->_integral += this->_ki * error * this->_dt;
    if (this->_integral > this->_maxOutput) this->_integral = this->_maxOutput;
    else if (this->_integral < this->_minOutput) this->_integral = this->_minOutput;

    // Derivative term
    double derivative = 0.0;
    if (this->_dt > 0) {
        derivative = (error - this->_previousError) / this->_dt;
    }

    // PID raw output
    double raw = this->_kp * error + this->_integral + this->_kd * derivative;

    // Deadband compensation
    double compensated = this->applyDeadband(raw);

    // Clamp final output
    double output = compensated;
    if (output > this->_maxOutput) output = this->_maxOutput;
    else if (output < this->_minOutput) output = this->_minOutput;

    this->_previousError = error;
    return output;
}

void PID::reset() {
    this->_integral = 0.0;
    this->_previousError = 0.0;
    this->_lastTime = micros();
}
