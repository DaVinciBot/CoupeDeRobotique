#ifndef ROLLING_BASIS_H
#define ROLLING_BASIS_H

#include <chrono>
#include "motor.h"
#include "pid.h"
#include "point.h"

class RollingBasis {
   public:
    enum class Phase { Idle, Rotating, Forwarding, Done };
    RollingBasis(Motor* leftMotor,
                 Motor* rightMotor,
                 float wheelDiameterMm,
                 float wheelBaseMm,
                 const Point& initialPosition = {0, 0, 0});

    void setCommand(const Point& target);

    void update();

    bool isMoving() const;
    void stop();

    Point getPose() const;
    float getLinearSpeedMmPerS() const;
    float getAngularSpeedRadPerS() const;

   private:
    // void _computeOdometry(float dt);
    // void _applyControl(float dt);
    float _wrapToPi(float ang) const;
    void _sendWheelSpeeds(float v, float w);

    Motor* _leftMotor;
    Motor* _rightMotor;
    float _wheelDiameterMm;
    float _wheelBaseMm;

    // long _prevLeftSteps;
    // long _prevRightSteps;

    Point _currentPose;
    float _linearSpeed;
    float _angularSpeed;
    Phase _phase;

    // computed plan
    float _rotateDuration;
    float _forwardDuration;
    float _rotateDirection;
    std::chrono::steady_clock::time_point _startTime;

    // PID _linDistPid, _angDistPid;

    // float _cmdLinSpeed;
    // float _cmdAngSpeed;
    // Point _cmdPosition;

    // float _measLinSpeed;
    // float _measAngSpeed;

    // std::chrono::steady_clock::time_point _lastTime;
    // bool _moving;
};

#endif
