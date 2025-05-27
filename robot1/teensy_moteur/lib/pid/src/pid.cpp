/**
 * This is the implementation of the PID class.
 * The PID class compute the error for the servo-control of the motors.
 */

#include <pid.h>
#include <Arduino.h>

PID::PID(double kp, double ki, double kd, double minOutput, double maxOutput)
    : _kp(kp), _ki(ki), _kd(kd), _minOutput(minOutput), _maxOutput(maxOutput),
      _integral(0.0), _previousError(0.0), _lastTime(micros()), _dt(0.0) {}

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

void PID::updateDeltaTime() {
    unsigned long now = micros();
    this->_dt = (now - this->_lastTime) * 1e-6;
    this->_lastTime = now;
}

double PID::compute(double error) {
    this->updateDeltaTime();

    // Integral term with anti-windup
    this->_integral += this->_ki * error * this->_dt;
    if (this->_integral > this->_maxOutput) this->_integral = this->_maxOutput;
    else if (this->_integral < this->_minOutput) this->_integral = this->_minOutput;

    // Derivative term
    double derivative = 0.0;
    if (this->_dt > 0) {
        derivative = (error - this->_previousError) / this->_dt;
    }

    // PID output before clamping
    double output = this->_kp * error + this->_integral + this->_kd * derivative;

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
