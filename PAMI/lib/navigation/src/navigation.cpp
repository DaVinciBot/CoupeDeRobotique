#include "navigation.h"

Navigation::Navigation(Motor* leftMotor, Motor* rightMotor, float wheelDiameterMm, float wheelBaseMm) {
    _leftMotor = leftMotor;
    _rightMotor = rightMotor;
    _wheelDiameterMm = wheelDiameterMm;
    _wheelBaseMm = wheelBaseMm;
    _moving = false;
    _turning = false;
    _leftSteps = 0;
    _rightSteps = 0;
}

void Navigation::forward(float distanceMm) {
    
    _leftMotor->moveDistance(distanceMm, _wheelDiameterMm);
    _rightMotor->moveDistance(distanceMm, _wheelDiameterMm);

    _turning = false;
    _moving = true;
}

void Navigation::turn(float angleDeg) {
    float arcLength = M_PI * _wheelBaseMm * fabs(angleDeg) / 360.0f;

    bool turnLeft = (angleDeg > 0);

    float leftDist =  turnLeft ? -arcLength : arcLength;
    float rightDist = turnLeft ? arcLength : -arcLength;

    _leftMotor->moveDistance(leftDist, _wheelDiameterMm);
    _rightMotor->moveDistance(rightDist, _wheelDiameterMm);

    _turning = true;
    _moving = true;
}

void Navigation::update() {
    if(!_moving) return;

    _leftMotor->update();
    _rightMotor->update();

    if(!_leftMotor->isMoving() && !_rightMotor->isMoving()) {
        _moving = false;
        _turning = false;
    }
}

void Navigation::stop() {
    _leftMotor->setTargetSpeed(0);
    _rightMotor->setTargetSpeed(0);
    _leftMotor->enableMotor(false);
    _rightMotor->enableMotor(false);
}