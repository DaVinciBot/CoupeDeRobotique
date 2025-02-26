#ifndef NAVIGATION_H
#define NAVIGATION_H

#include "motors.h"

class Navigation
{
private:
    Motor *_leftMotor;
    Motor *_rightMotor;
    float _wheelDiameterMm;
    float _wheelBaseMm;

    float _linearSpeedMmS;
    float _angularSpeedDegS;

public:
    Navigation(Motor *leftMotor, Motor *rightMotor, float wheelDiameterMm, float wheelBaseMm);
    ~Navigation() = default;

    void setLinearAngularSpeed(float linearMmS, float angularDegS);
    void update();
    bool isBusy() const;
    void stop();
};

#endif