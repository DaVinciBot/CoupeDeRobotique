#include "navigation.h"
#include <math.h>

Navigation::Navigation(Motor *leftMotor, Motor *rightMotor, float wheelDiameterMm, float wheelBaseMm)
    : _leftMotor(leftMotor), _rightMotor(rightMotor),
      _wheelDiameterMm(wheelDiameterMm), _wheelBaseMm(wheelBaseMm),
      _linearSpeedMmS(0), _angularSpeedDegS(0)
{
}

void Navigation::setLinearAngularSpeed(float linearMmS, float angularDegS)
{
    _linearSpeedMmS = linearMmS;
    _angularSpeedDegS = angularDegS;

    float angularRadS = _angularSpeedDegS * (M_PI / 180.0f);
    float halfBase = _wheelBaseMm / 2.0f;

    float leftVel = _linearSpeedMmS - (angularRadS * halfBase);
    float rightVel = _linearSpeedMmS + (angularRadS * halfBase);

    float circumference = M_PI * _wheelDiameterMm;
    float leftStepsPerSec = (leftVel / circumference) * _leftMotor->getStepsPerRev();
    float rightStepsPerSec = (rightVel / circumference) * _rightMotor->getStepsPerRev();

    _leftMotor->setTargetSpeed(leftStepsPerSec);
    _rightMotor->setTargetSpeed(rightStepsPerSec);
}

void Navigation::update()
{
    _leftMotor->update();
    _rightMotor->update();
}

bool Navigation::isBusy() const
{
    return _leftMotor->isMoving() || _rightMotor->isMoving();
}

void Navigation::stop()
{
    _linearSpeedMmS = 0;
    _angularSpeedDegS = 0;
    _leftMotor->setTargetSpeed(0);
    _rightMotor->setTargetSpeed(0);
}