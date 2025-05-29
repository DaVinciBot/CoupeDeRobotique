#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>

class Motor
{
public:
    Motor(byte stepPin, byte dirPin, byte enablePin, unsigned int stepsPerRevolution, float k);
    ~Motor() = default;

    void init();
    void enableMotor(bool enable);

    void setTargetSpeed(float stepsPerSec);
    void setAcceleration(float stepsPerSec2);
    void update();

    unsigned int getStepsPerRev() const;
    bool isMoving() const;

    long getStepCount() const;
    void resetStepCount();

private:
    byte _stepPin;
    byte _dirPin;
    byte _enablePin;
    float _factorK;

    unsigned int _stepsPerRevolution;
    float _targetSpeedStepsPerSec;
    float _currentSpeedStepsPerSec;
    float _acceleration;

    bool _moving;
    unsigned long _lastStepTime;
    float _usDelayBetweenKSteps;
    long _stepCount;

    void _setDirection(bool clockwise);
    void _doKSteps();
};

#endif