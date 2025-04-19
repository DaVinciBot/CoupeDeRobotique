#ifndef ROLLING_BASIS_H
#define ROLLING_BASIS_H

#include "motor.h"
#include "pid.h"
#include "structures.h"
#include <chrono>

class RollingBasis
{
public:
    RollingBasis(Motor *leftMotor, Motor *rightMotor,
                 float wheelDiameterMm,
                 float wheelBaseMm,
                 const PID &linearSpeedPid,
                 const PID &angularSpeedPid,
                 const PID &linearDistancePid,
                 const PID &angularDistancePid);

    void setLinearAngularSpeed(float linearSpeedMmPerS, float angularSpeedRadPerS);

    void setTargetPosition(Point targetPosition);

    void update();

    bool isMoving() const;
    void stop();

    Point getPose() const;
    float getMeasuredLinearSpeedMmPerS() const;
    float getMeasuredAngularSpeedRadPerS() const;
    float getMeasuredLinearDistanceMm() const;
    float getMeasuredAngularDistanceRad() const;

    void resetPose();

private:
    void _computeOdometry(float dt);
    void _applyControl(float dt);

    Motor *_leftMotor;
    Motor *_rightMotor;
    float _wheelDiameterMm;
    float _wheelBaseMm;

    long _previousLeftStepCount;
    long _previousRightStepCount;

    float _x;     // mm
    float _y;     // mm
    float _theta; // rad

    PID _linearSpeedPid;
    PID _angularSpeedPid;
    PID _linearDistancePid;
    PID _angularDistancePid;

    float _targetLinearSpeedMmPerS;
    float _targetAngularSpeedRadPerS;
    Point _targetPosition;

    float _measuredLinearSpeedMmPerS;
    float _measuredAngularSpeedRadPerS;
    float _measuredLinearDistanceMm;
    float _measuredAngularDistanceRad;

    std::chrono::steady_clock::time_point _lastUpdateTime;
};

#endif