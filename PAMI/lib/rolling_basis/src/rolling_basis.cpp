#include "rolling_basis.h"
#include <math.h>

RollingBasis::RollingBasis(Motor *leftMotor, Motor *rightMotor,
                           float wheelDiameterMm,
                           float wheelBaseMm,
                           const PID &linearSpeedPid,
                           const PID &angularSpeedPid,
                           const PID &linearDistancePid,
                           const PID &angularDistancePid)
    : _leftMotor(leftMotor), _rightMotor(rightMotor),
      _wheelDiameterMm(wheelDiameterMm), _wheelBaseMm(wheelBaseMm),
      _previousLeftStepCount(0), _previousRightStepCount(0),
      _x(0), _y(0), _theta(0),
      _linearSpeedPid(linearSpeedPid),
      _angularSpeedPid(angularSpeedPid),
      _linearDistancePid(linearDistancePid),
      _angularDistancePid(angularDistancePid),
      _targetLinearSpeedMmPerS(0), _targetAngularSpeedRadPerS(0),
      _targetPosition(Point(0, 0, 0)),
      _measuredLinearSpeedMmPerS(0), _measuredAngularSpeedRadPerS(0),
      _lastUpdateTime(std::chrono::steady_clock::now())
{
    _leftMotor->resetStepCount();
    _rightMotor->resetStepCount();
}

void RollingBasis::setLinearAngularSpeed(float linearSpeed, float angularSpeed)
{
    _targetLinearSpeedMmPerS = linearSpeed;
    _targetAngularSpeedRadPerS = angularSpeed;

    _linearSpeedPid.reset();
    _angularSpeedPid.reset();
}

void RollingBasis::setTargetPosition(Point targetPosition)
{
    _targetPosition = targetPosition;

    _linearDistancePid.reset();
    _angularDistancePid.reset();
}

void RollingBasis::update()
{
    auto now = std::chrono::steady_clock::now();
    float dt = std::chrono::duration<float>(now - _lastUpdateTime).count();
    if (dt <= 0)
        return;

    _computeOdometry(dt);
    _applyControl(dt);

    _leftMotor->update();
    _rightMotor->update();

    _lastUpdateTime = now;
}

void RollingBasis::_computeOdometry(float dt)
{
    long leftSteps = _leftMotor->getStepCount();
    long rightSteps = _rightMotor->getStepCount();

    long dL = leftSteps - _previousLeftStepCount;
    long dR = rightSteps - _previousRightStepCount;
    _previousLeftStepCount = leftSteps;
    _previousRightStepCount = rightSteps;

    float mmPerStep = (M_PI * _wheelDiameterMm) / _leftMotor->getStepsPerRev();
    float dLeft = dL * mmPerStep;
    float dRight = dR * mmPerStep;

    float dCenter = (dLeft + dRight) / 2.0f;
    float dTheta = (dRight - dLeft) / _wheelBaseMm;

    _x += dCenter * cosf(_theta + dTheta / 2.0f);
    _y += dCenter * sinf(_theta + dTheta / 2.0f);
    _theta = fmodf(_theta + dTheta, 2 * M_PI);

    _measuredLinearSpeedMmPerS = dCenter / dt;
    _measuredAngularSpeedRadPerS = dTheta / dt;
}

void RollingBasis::_applyControl(float dt)
{
    _linearSpeedPid->setSampleTime(dt);
    _angularSpeedPid->setSampleTime(dt);
    _linearDistancePid.setSampleTime(dt);
    _angularDistancePid.setSampleTime(dt);

    // _linearSpeedPid.setOutputLimits(-_targetLinearSpeedMmPerS, _targetLinearSpeedMmPerS);
    // _angularSpeedPid.setOutputLimits(-_targetAngularSpeedRadPerS, _targetAngularSpeedRadPerS);
    // if (_useDistanceControl)
    // {
    //     _linearDistancePid.setOutputLimits(-_targetLinearDistance, _targetLinearDistance);
    //     _angularDistancePid.setOutputLimits(-_targetAngularDistance, _targetAngularDistance);
    // }

    float linearSpeedError = _targetLinearSpeedMmPerS - _measuredLinearSpeedMmPerS;
    float angularSpeedError = _targetAngularSpeedRadPerS - _measuredAngularSpeedRadPerS;
    float linearDistanceError = sqrt(pow(target_position.x - _x, 2) + pow(target_position.y - _y, 2));
    float angularDistanceError = target_position.theta - fmodf(_theta, 2 * M_PI);

    float linearSpeedCorrection = _linearSpeedPid.compute(linearSpeedError);
    float angularSpeedCorrection = _angularSpeedPid.compute(angularSpeedError);
    float linearDistanceCorrection = _linearDistancePid.compute(linearDistanceError);
    float angularDistanceCorrection = _angularDistancePid.compute(angularDistanceError);

    float linearCmd = _targetLinearSpeedMmPerS + linearSpeedCorrection;
    float angularCmd = _targetAngularSpeedRadPerS + angularSpeedCorrection;

    float halfBase = _wheelBaseMm / 2.0f;
    float leftSpeedMmPerSec = linearCmd - angularCmd * halfBase;
    float rightSpeedMmPerSec = linearCmd + angularCmd * halfBase;

    float circumference = M_PI * _wheelDiameterMm;
    float leftSpeedStepsPerSec = (leftSpeedMmPerSec / circumference) * _leftMotor->getStepsPerRev();
    float rightSpeedStepsPerSec = (rightSpeedMmPerSec / circumference) * _rightMotor->getStepsPerRev();

    _leftMotor->setTargetSpeed(leftSpeedStepsPerSec);
    _rightMotor->setTargetSpeed(rightSpeedStepsPerSec);
}

bool RollingBasis::isMoving() const { return _leftMotor->isMoving() || _rightMotor->isMoving(); }

void RollingBasis::stop()
{
    _targetLinearSpeedMmPerS = 0;
    _targetAngularSpeedRadPerS = 0;
    _targetPosition = Point(0, 0, 0);

    _linearSpeedPid.reset();
    _angularSpeedPid.reset();
    _linearDistancePid->reset();
    _angularDistancePid->reset();

    _leftMotor->setTargetSpeed(0);
    _rightMotor->setTargetSpeed(0);
}

Point RollingBasis::getPose() const
{
    return Point(_x, _y, _theta);
}
float RollingBasis::getMeasuredLinearSpeedMmPerS() const { return _measuredLinearSpeedMmPerS; }
float RollingBasis::getMeasuredAngularSpeedRadPerS() const { return _measuredAngularSpeedRadPerS; }

void RollingBasis::resetPose()
{
    _x = _y = _theta = 0;
    _previousLeftStepCount = _previousRightStepCount = 0;
    _leftMotor->resetStepCount();
    _rightMotor->resetStepCount();
    _linearSpeedPid->reset();
    _angularSpeedPid->reset();
    _linearDistancePid->reset();
    _angularDistancePid->reset();
}