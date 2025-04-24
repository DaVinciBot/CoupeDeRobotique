#include "rolling_basis.h"
#include <math.h>

RollingBasis::RollingBasis(Motor *leftMotor, Motor *rightMotor,
                           float wheelDiameterMm,
                           float wheelBaseMm,
                           const PID &linearSpeedPid,
                           const PID &angularSpeedPid,
                           const PID &linearDistancePid,
                           const PID &angularDistancePid,
                           const Point &initialPosition)
    : _leftMotor(leftMotor), _rightMotor(rightMotor),
      _wheelDiameterMm(wheelDiameterMm), _wheelBaseMm(wheelBaseMm),
      _prevLeftSteps(0),
      _prevRightSteps(0),
      _currentPosition(initialPosition),
      _linSpeedPid(linearSpeedPid),
      _angSpeedPid(angularSpeedPid),
      _linDistPid(linearDistancePid),
      _angDistPid(angularDistancePid),
      _cmdLinSpeed(0), _cmdAngSpeed(0),
      _cmdPosition{0, 0, 0},
      _measLinSpeed(0), _measAngSpeed(0),
      _lastTime(std::chrono::steady_clock::now())
{
    _leftMotor->resetStepCount();
    _rightMotor->resetStepCount();
}

void RollingBasis::setCommand(float linearSpeedMmPerS,
                              float angularSpeedRadPerS,
                              const Point &targetPosition)
{
    _cmdLinSpeed = linearSpeedMmPerS;
    _cmdAngSpeed = angularSpeedRadPerS;
    _cmdPosition = targetPosition;

    _linSpeedPid.reset();
    _angSpeedPid.reset();
    _linDistPid.reset();
    _angDistPid.reset();
}

void RollingBasis::update()
{
    auto now = std::chrono::steady_clock::now();
    float dt = std::chrono::duration<float>(now - _lastTime).count();
    if (dt <= 0)
        return;

    computeOdometry(dt);
    applyControl(dt);

    _leftMotor->update();
    _rightMotor->update();
    _lastTime = now;
}

void RollingBasis::computeOdometry(float dt)
{
    long leftSteps = _leftMotor->getStepCount();
    long rightSteps = _rightMotor->getStepCount();
    long dL = leftSteps - _prevLeftSteps;
    long dR = rightSteps - _prevRightSteps;
    _prevLeftSteps = leftSteps;
    _prevRightSteps = rightSteps;

    float mmPerStep = (M_PI * _wheelDiameterMm) / _leftMotor->getStepsPerRev();
    float dLeft = dL * mmPerStep;
    float dRight = dR * mmPerStep;

    float dCenter = 0.5f * (dLeft + dRight);
    float dTheta = (dRight - dLeft) / _wheelBaseMm;

    _currentPosition.x += dCenter * cosf(_currentPosition.theta + dTheta / 2.0f);
    _currentPosition.y += dCenter * sinf(_currentPosition.theta + dTheta / 2.0f);
    _currentPosition.theta = wrapToPi(_currentPosition.theta + dTheta);

    _measLinSpeed = dCenter / dt;
    _measAngSpeed = dTheta / dt;
}

void RollingBasis::applyControl(float dt)
{
    _linSpeedPid.setSampleTime(dt);
    _angSpeedPid.setSampleTime(dt);
    _linDistPid.setSampleTime(dt);
    _angDistPid.setSampleTime(dt);

    float distErr = Point::distance(_currentPosition, _cmdPosition);                            // mm
    float be = wrapToPi(Point::angle(_currentPosition, _cmdPosition) - _currentPosition.theta); // rad
    float oe = wrapToPi(_cmdPosition.theta - _currentPosition.theta);                           // rad
    float bearErr = wrapToPi(be + oe);                                                          // rad

    float corrLinD = _linDistPid.compute(distErr) / dt; // mm/s
    float corrAngD = _angDistPid.compute(bearErr) / dt; // rad/s

    float spdLinRef = _cmdLinSpeed + corrLinD;
    float spdAngRef = _cmdAngSpeed + corrAngD;

    float corrLinS = _linSpeedPid.compute(spdLinRef - _measLinSpeed);
    float corrAngS = _angSpeedPid.compute(spdAngRef - _measAngSpeed);

    float cmdLin = spdLinRef + corrLinS;
    float cmdAng = spdAngRef + corrAngS;

    float halfBase = _wheelBaseMm * 0.5f;
    float leftSpeedMmPerSec = cmdLin - cmdAng * halfBase;
    float rightSpeedMmPerSec = cmdLin + cmdAng * halfBase;

    float circumference = M_PI * _wheelDiameterMm;
    float leftSpeedStepsPerSec = (leftSpeedMmPerSec / circumference) * _leftMotor->getStepsPerRev();
    float rightSpeedStepsPerSec = (rightSpeedMmPerSec / circumference) * _rightMotor->getStepsPerRev();

    _leftMotor->setTargetSpeed(leftSpeedStepsPerSec);
    _rightMotor->setTargetSpeed(rightSpeedStepsPerSec);
}

float RollingBasis::wrapToPi(float ang) const
{
    while (ang > M_PI)
        ang -= 2 * M_PI;
    while (ang < -M_PI)
        ang += 2 * M_PI;
    return ang;
}

bool RollingBasis::isMoving() const
{
    return _leftMotor->isMoving() || _rightMotor->isMoving();
}

void RollingBasis::stop()
{
    _cmdLinSpeed = _cmdAngSpeed = 0;
    _cmdPosition = {0, 0, 0};
    _leftMotor->setTargetSpeed(0);
    _rightMotor->setTargetSpeed(0);
    _linSpeedPid.reset();
    _angSpeedPid.reset();
    _linDistPid.reset();
    _angDistPid.reset();
}

Point RollingBasis::getPose() const
{
    return _currentPosition;
}

// QUESTION: ou :
// const Point &RollingBasis::getPose() const
// {
//     return _currentPosition;
// } ?

float RollingBasis::getMeasuredLinearSpeedMmPerS() const { return _measLinSpeed; }
float RollingBasis::getMeasuredAngularSpeedRadPerS() const { return _measAngSpeed; }
