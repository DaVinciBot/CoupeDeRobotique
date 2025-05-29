#include "motor.h"

Motor::Motor(byte stepPin, byte dirPin, byte enablePin, unsigned int stepsPerRevolution, float k)
{
    this->_stepPin = stepPin;
    this->_dirPin = dirPin;
    this->_enablePin = enablePin;
    this->_factorK = k;

    this->_stepsPerRevolution = stepsPerRevolution / k; // Divide by k to get the actual steps per revolution
    this->_targetSpeedStepsPerSec = 0.0f;
    this->_currentSpeedStepsPerSec = 0.0f;
    this->_acceleration = 0.0f;
    this->_moving = false;

    this->_lastStepTime = 0;
    this->_usDelayBetweenKSteps = 0.0f;
    this->_stepCount = 0;
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
    _targetSpeedStepsPerSec = stepsPerSec;
    _moving = (fabs(_targetSpeedStepsPerSec) >= 1.0f);
    enableMotor(_moving);
}

void Motor::setAcceleration(float stepsPerSec2)
{
    _acceleration = max(0.0f, stepsPerSec2);
}

void Motor::_setDirection(bool clockwise)
{
    if (_dirPin == 0 || _dirPin == -1)
        return; // No enable pin, do nothing
    digitalWrite(_dirPin, clockwise ? HIGH : LOW);
}

void Motor::_doKSteps()
{
    for (int i = 0; i < _factorK; ++i)
    {
        digitalWrite(_stepPin, HIGH);
        delayMicroseconds(500);
        digitalWrite(_stepPin, LOW);
        delayMicroseconds(500);
    }

    if (_currentSpeedStepsPerSec >= 0)
    {
        _stepCount++;
    }
    else
    {
        _stepCount--;
    }
}

void Motor::update()
{
    if (!_moving)
        return;

    unsigned long now = micros();
    unsigned long dt = now - _lastStepTime;
    float dtSec = dt * 1e-6f;
    float speedDiff = _acceleration * dtSec;

    if (fabs(_currentSpeedStepsPerSec - _targetSpeedStepsPerSec) < speedDiff)
    {
        _currentSpeedStepsPerSec = _targetSpeedStepsPerSec;
    }
    else if (_currentSpeedStepsPerSec < _targetSpeedStepsPerSec)
    {
        _currentSpeedStepsPerSec += speedDiff;
    }
    else if (_currentSpeedStepsPerSec > _targetSpeedStepsPerSec)
    {
        _currentSpeedStepsPerSec -= speedDiff;
    }

    if (fabs(_currentSpeedStepsPerSec) < 1.0f)
    {
        _usDelayBetweenKSteps = 1e6f;
    }
    else
    {
        _usDelayBetweenKSteps = (_factorK * 1e6f) / fabs(_currentSpeedStepsPerSec);
    }

    bool clockwise = (_currentSpeedStepsPerSec >= 0);
    _setDirection(clockwise);

    if (dt >= _usDelayBetweenKSteps)
    {
        _doKSteps();
        _lastStepTime = now;
    }

    if (fabs(_targetSpeedStepsPerSec) < 1.0f && fabs(_currentSpeedStepsPerSec) < 1.0f)
    {
        _moving = false;
        enableMotor(false);
    }
}

bool Motor::isMoving() const
{
    return _moving;
}

unsigned int Motor::getStepsPerRev() const
{
    return _stepsPerRevolution;
}

long Motor::getStepCount() const
{
    return _stepCount;
}

void Motor::resetStepCount()
{
    _stepCount = 0;
}
