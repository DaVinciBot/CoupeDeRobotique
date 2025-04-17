#ifndef ROLLING_BASIS_H
#define ROLLING_BASIS_H

#include "motors.h"

class RollingBasis
{
public:
    RollingBasis(Motor *leftMotor, Motor *rightMotor,
                 float wheelDiameterMm, float wheelBaseMm);

    void setLinearAngularSpeed(float linearMmS, float angularDegS);
    void update();

    bool isMoving() const;
    void stop();

    void getPose(float &x, float &y, float &theta) const;
    void resetPose();

private:
    Motor *_leftMotor;
    Motor *_rightMotor;
    float _wheelDiameterMm;
    float _wheelBaseMm;

    long _previousLeftStepCount;
    long _lastRightStepCount;

    float _x, _y, _theta;
};

#endif