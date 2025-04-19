#ifndef ROLLING_BASIS_H
#define ROLLING_BASIS_H

#include "motor.h"
#include "pid.h"
#include "point.h"
#include <chrono>

class RollingBasis
{
public:
    RollingBasis(Motor *leftMotor,
                 Motor *rightMotor,
                 float wheelDiameterMm,
                 float wheelBaseMm,
                 const PID &linearSpeedPid,
                 const PID &angularSpeedPid,
                 const PID &linearDistancePid,
                 const PID &angularDistancePid,
                 const Point &initialPosition = {0, 0, 0});

    void setCommand(float linearSpeedMmPerS,
                    float angularSpeedRadPerS,
                    const Point &targetPosition);

    void update();

    bool isMoving() const;
    void stop();

    Point getPose() const;
    // QUESTION: ou : const Point &RollingBasis::getPose() const; ?
    float getMeasuredLinearSpeedMmPerS() const;
    float getMeasuredAngularSpeedRadPerS() const;

private:
    void computeOdometry(float dt);
    void applyControl(float dt);
    float wrapToPi(float ang) const;

    Motor *_leftMotor;
    Motor *_rightMotor;
    float _wheelDiameterMm;
    float _wheelBaseMm;

    long _prevLeftSteps;
    long _prevRightSteps;

    Point _currentPosition;

    PID _linSpeedPid, _angSpeedPid;
    PID _linDistPid, _angDistPid;

    float _cmdLinSpeed;
    float _cmdAngSpeed;
    Point _cmdPosition;

    float _measLinSpeed;
    float _measAngSpeed;

    std::chrono::steady_clock::time_point _lastTime;
};

#endif
