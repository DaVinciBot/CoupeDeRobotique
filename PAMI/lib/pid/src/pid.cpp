#include "pid.h"

PID::PID(float kp, float ki, float kd, float dtSeconds)
    : _kp(kp),
      _ki(ki),
      _kd(kd),
      _dtSeconds(dtSeconds),
      _integral(0.0f),
      _previousError(0.0f) {}

float PID::compute(float error) {
    _integral += error * _dtSeconds;
    float derivative = (error - _previousError) / _dtSeconds;
    float output = _kp * error + _ki * _integral + _kd * derivative;

    _previousError = error;
    return output;
}

void PID::reset() {
    _integral = 0.0f;
    _previousError = 0.0f;
}

void PID::setTunings(float kp, float ki, float kd) {
    _kp = kp;
    _ki = ki;
    _kd = kd;
}

void PID::setSampleTime(float dtSeconds) {
    _dtSeconds = dtSeconds;
}
