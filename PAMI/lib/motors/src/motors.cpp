#include "motors.h"

Motor::Motor(byte stepPin, byte dirPin, byte enablePin, unsigned int stepsPerRevolution)
    : _stepPin(stepPin), _dirPin(dirPin), _enablePin(enablePin), _stepsPerRev(stepsPerRevolution)
{
    _targetSpeedStepsPerSec = 0.0f;
    _currentSpeedStepsPerSec = 0.0f;
    _acceleration = 0.0f;
    _moving = false;
    _lastStepTime = 0;
    _stepIntervalUs = 0.0f;
}

void Motor::init()
{
    pinMode(_stepPin, OUTPUT);
    pinMode(_dirPin, OUTPUT);
    pinMode(_enablePin, OUTPUT);
    enableMotor(false);
}

void Motor::enableMotor(bool enable)
{
    digitalWrite(_enablePin, enable ? LOW : HIGH);
}

void Motor::setTargetSpeed(float stepsPerSec)
{
    if (stepsPerSec < 0)
        stepsPerSec = 0;
    _targetSpeedStepsPerSec = stepsPerSec;
    _moving = (_targetSpeedStepsPerSec > 0);
}

void Motor::setAcceleration(float stepsPerSec2)
{
    if (stepsPerSec2 < 0)
        stepsPerSec2 = 0;
    _acceleration = stepsPerSec2;
}

void Motor::_setDirection(bool clockwise)
{
    digitalWrite(_dirPin, clockwise ? HIGH : LOW);
}

void Motor::_doOneStep()
{
    digitalWrite(_stepPin, HIGH);
    delayMicroseconds(2);
    digitalWrite(_stepPin, LOW);
}

void Motor::update()
{
    if (!_moving)
        return;

    unsigned long now = micros();
    unsigned long dt = now - _lastStepTime;
    float dtSec = dt / 1000000.0f;
    float speedDiff = _acceleration * dtSec;

    if (_currentSpeedStepsPerSec < _targetSpeedStepsPerSec)
    {
        _currentSpeedStepsPerSec += speedDiff;
        if (_currentSpeedStepsPerSec > _targetSpeedStepsPerSec)
        {
            _currentSpeedStepsPerSec = _targetSpeedStepsPerSec;
        }
    }
    else if (_currentSpeedStepsPerSec > _targetSpeedStepsPerSec)
    {
        _currentSpeedStepsPerSec -= speedDiff;
        if (_currentSpeedStepsPerSec < _targetSpeedStepsPerSec)
        {
            _currentSpeedStepsPerSec = _targetSpeedStepsPerSec;
        }
    }

    if (_currentSpeedStepsPerSec < 1.0f)
    {
        _stepIntervalUs = 1e6;
    }
    else
    {
        _stepIntervalUs = 1e6 / _currentSpeedStepsPerSec;
    }

    bool clockwise = (_currentSpeedStepsPerSec >= 0);
    _setDirection(clockwise);

    if (dt >= _stepIntervalUs)
    {
        _doOneStep();
        _lastStepTime = micros();
    }

    // Stoppage si target = 0
    if (_targetSpeedStepsPerSec < 1.0f && _currentSpeedStepsPerSec < 1.0f)
    {
        _moving = false;
    }
}