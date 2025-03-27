#ifndef MOTORS_H
#define MOTORS_H

#include <Arduino.h>

class Motor
{
private:
    byte _stepPin;
    byte _dirPin;
    byte _enablePin;

    unsigned int _stepsPerRev;
    float _targetSpeedStepsPerSec;
    float _currentSpeedStepsPerSec;
    float _acceleration;

    bool _moving;
    unsigned long _lastStepTime;
    float _usDelayBetweenTenSteps;

    void _setDirection(bool clockwise);
    void _doTenSteps();

public:
    Motor(byte stepPin, byte dirPin, byte enablePin, unsigned int stepsPerRevolution);
    ~Motor() = default;

    void init();
    void enableMotor(bool enable);

    void setTargetSpeed(float stepsPerSec);
    void setAcceleration(float stepsPerSec2);
    void update();

    unsigned int getStepsPerRev() const { return _stepsPerRev; }
    bool isMoving() const { return _moving; }
};

#endif