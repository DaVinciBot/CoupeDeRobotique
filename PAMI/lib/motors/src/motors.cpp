#include "motors.h"

Motor::Motor(byte stepPin, byte dirPin, byte enablePin, unsigned int stepsPerRevolution) {
    _stepPin = stepPin;
    _dirPin = dirPin;
    _enablePin = enablePin;
    _stepsPerRev = stepsPerRevolution;
    _targetSpeed = 0.0f;
    _currentSpeed = 0.0f;
    _acceleration = 0.0f;
    _moving = false;
    _stepsRemaining = 0;
    _lastStepTime = 0;
    _stepIntervalUs = 0.0f;
}

void Motor::init() {
    pinMode(_stepPin, OUTPUT);
    pinMode(_dirPin, OUTPUT);
    pinMode(_enablePin, OUTPUT);
    enableMotor(false);
}

void Motor::enableMotor(bool enable) {
    digitalWrite(_enablePin, enable ? LOW : HIGH);
    // digitalWrite(_enablePin, enable ? HIGH : LOW); demander à l'elec le branchement
}

void Motor::setTargetSpeed(float stepsPerSec) {
    if(stepsPerSec < 0) stepsPerSec = 0;
    _targetSpeed = stepsPerSec;
}

void Motor::setAcceleration(float accel) {
    if(accel < 0) accel = 0;
    _acceleration = accel;
}

void Motor::moveSteps(long steps) {
    bool clockwise = (steps >= 0);
    long nbSteps = labs(steps);

    _setDirection(clockwise);

    _stepsRemaining = nbSteps;

    _moving = true;

    _lastStepTime = micros();
    if(_currentSpeed < 1.0f) {
        _stepIntervalUs = 1000000.0f;
    } else {
        _stepIntervalUs = 1000000.0f / _currentSpeed;
    }
}

void Motor::moveDistance(float distanceMm, float wheelDiameterMm) {
    float circumference = M_PI * wheelDiameterMm;
    float turns = distanceMm / circumference;
    long steps = (long)(turns * _stepsPerRev);
    moveSteps(steps);
}

void Motor::update() {
    if(!_moving || _stepsRemaining <= 0) {
        _moving = false;
        return;
    }

    unsigned long now = micros();
    unsigned long dt = now - _lastStepTime;

    float dtSec = (float)dt / 1000000.0f;
    float speedDiff = _acceleration * dtSec;

    if(_currentSpeed < _targetSpeed) {
        _currentSpeed += speedDiff;
        if(_currentSpeed > _targetSpeed) {
            _currentSpeed = _targetSpeed;
        }
    } else if(_currentSpeed > _targetSpeed) {
        _currentSpeed -= speedDiff;
        if(_currentSpeed < _targetSpeed) {
            _currentSpeed = _targetSpeed;
        }
    }

    if(_currentSpeed < 1.0f) {
        _stepIntervalUs = 1000000.0f; // 1 s
    } else {
        _stepIntervalUs = 1000000.0f / _currentSpeed;
    }

    if(dt >= _stepIntervalUs) {
        _doOneStep();

        _lastStepTime = micros();
        _stepsRemaining--;

        if(_stepsRemaining <= 0) {
            _moving = false;
        }
    }
}

void Motor::_setDirection(bool clockwise) {
    digitalWrite(_dirPin, clockwise ? HIGH : LOW);
}

void Motor::_doOneStep() {
    digitalWrite(_stepPin, HIGH);
    delayMicroseconds(2); // ?????
    digitalWrite(_stepPin, LOW);
}