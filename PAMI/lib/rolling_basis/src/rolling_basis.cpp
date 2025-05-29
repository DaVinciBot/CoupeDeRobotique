#include "rolling_basis.h"
#include <math.h>

#define POSITION_TOLERANCE_MM 1.0f    // 1 mm
#define ANGLE_TOLERANCE_RAD 0.01f    // env. 0.57°
#define MAX_LINEAR_SPEED_MM_PER_S 100.0f
#define MAX_ANGULAR_SPEED_RAD_PER_S 10.0f

RollingBasis::RollingBasis(Motor *leftMotor, Motor *rightMotor,
                           float wheelDiameterMm,
                           float wheelBaseMm,
                           const PID &linearDistancePid,
                           const PID &angularDistancePid,
                           const Point &initialPosition)
    : _leftMotor(leftMotor), _rightMotor(rightMotor),
      _wheelDiameterMm(wheelDiameterMm), _wheelBaseMm(wheelBaseMm),
      _prevLeftSteps(0),
      _prevRightSteps(0),
      _currentPosition(initialPosition),
      _linDistPid(linearDistancePid),
      _angDistPid(angularDistancePid),
      _cmdLinSpeed(0), _cmdAngSpeed(0),
      _cmdPosition{0, 0, 0},
      _measLinSpeed(0), _measAngSpeed(0),
      _lastTime(std::chrono::steady_clock::now()),
      _moving(false)
{
    _leftMotor->init();
    _rightMotor->init();
    _leftMotor->resetStepCount();
    _rightMotor->resetStepCount();
    _leftMotor->setAcceleration(100.0f);
    _rightMotor->setAcceleration(100.0f);
}

void RollingBasis::setCommand(const Point &targetPosition){
    _cmdPosition = targetPosition;

    _linDistPid.reset();
    _angDistPid.reset();
    _moving = true;
    
    Serial.print("[Command] New target set: x=");
    Serial.print(_cmdPosition.x);
    Serial.print(" y=");
    Serial.print(_cmdPosition.y);
    Serial.print(" theta=");
    Serial.println(_cmdPosition.theta);
}

void RollingBasis::update()
{
    if (!_moving) {
        _cmdPosition = _currentPosition;
        return;
    }
    
    auto now = std::chrono::steady_clock::now();
    float dt = std::chrono::duration<float>(now - _lastTime).count();
    if (dt <= 0)
        return;

    _computeOdometry(dt);
    
    float distErr = Point::distance(_currentPosition, _cmdPosition);
    float bearErr = _wrapToPi(_cmdPosition.theta - _currentPosition.theta);
    
    // Serial.print("[Update] Error: dist=");
    // Serial.print(distErr);
    // Serial.print(" bear=");
    // Serial.println(bearErr);

    if (distErr < POSITION_TOLERANCE_MM && std::fabs(bearErr) < ANGLE_TOLERANCE_RAD) {
        stop();
        return;
    }
    
    _applyControl(dt);

    _leftMotor->update();
    _rightMotor->update();
    _lastTime = now;
}

void RollingBasis::_computeOdometry(float dt)
{
    long leftSteps = _leftMotor->getStepCount();
    long rightSteps = -_rightMotor->getStepCount();
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
    _currentPosition.theta = _wrapToPi(_currentPosition.theta + dTheta);

    _measLinSpeed = dCenter / dt;
    _measAngSpeed = dTheta / dt;
    
    // Serial.print("[Odometry] dLeft=");
    // Serial.print(dLeft);
    // Serial.print(" dRight=");
    // Serial.print(dRight);
    // Serial.print(" dTheta=");
    // Serial.println(dTheta);
    Serial.print("[Odometry] New pose: x=");
    Serial.print(_currentPosition.x);
    Serial.print(" y=");
    Serial.print(_currentPosition.y);
    Serial.print(" theta=");
    Serial.println(_currentPosition.theta);
    Serial.print("[Odometry] Speeds: lin=");
    Serial.print(_measLinSpeed);
    Serial.print(" mm/s, ang=");
    Serial.print(_measAngSpeed);
    Serial.println(" rad/s");
}

void RollingBasis::_applyControl(float dt)
{
    _linDistPid.setSampleTime(dt);
    _angDistPid.setSampleTime(dt);

    float xerr = _cmdPosition.x - _currentPosition.x; // mm
    float yerr = _cmdPosition.y - _currentPosition.y; // mm

    float distErr = xerr * cosf(_currentPosition.theta) + yerr * sinf(_currentPosition.theta); // mm
    double mag = sqrt(pow(xerr, 2) + pow(yerr, 2));
    double sign = (distErr >= 0.0) ? +1.0 : -1.0;
    distErr = mag * sign;

    float bearErr = _wrapToPi(Point::angle(_cmdPosition, _currentPosition) - _currentPosition.theta);  // rad

    Serial.print("[Control] distErr=");
    Serial.print(distErr);
    Serial.print(" bearErr=");
    Serial.println(bearErr);
    
    float corrLinD = _linDistPid.compute(distErr); // mm/s
    float corrAngD = _angDistPid.compute(bearErr); // rad/s

    float spdLinRef = fmaxf(fminf(corrLinD, MAX_LINEAR_SPEED_MM_PER_S), -MAX_LINEAR_SPEED_MM_PER_S);
    float spdAngRef = fmaxf(fminf(corrAngD, MAX_ANGULAR_SPEED_RAD_PER_S), -MAX_ANGULAR_SPEED_RAD_PER_S);
    
    float cmdLin = spdLinRef;
    float cmdAng = spdAngRef;

    Serial.print("[Control] cmdLin=");
    Serial.print(cmdLin);
    Serial.print(" mm/s, cmdAng=");
    Serial.print(cmdAng);
    Serial.println(" rad/s");

    float halfBase = _wheelBaseMm * 0.5f;
    float leftSpeedMmPerSec = cmdLin - cmdAng * halfBase;
    float rightSpeedMmPerSec = cmdLin + cmdAng * halfBase;

    float circumference = M_PI * _wheelDiameterMm;
    float leftSpeedStepsPerSec = (leftSpeedMmPerSec / circumference) * _leftMotor->getStepsPerRev();
    float rightSpeedStepsPerSec = (rightSpeedMmPerSec / circumference) * _rightMotor->getStepsPerRev();

    Serial.print("[Control] leftSpeedStepsPerSec=");
    Serial.print(leftSpeedStepsPerSec);
    Serial.print(" rightSpeedStepsPerSec=");
    Serial.println(rightSpeedStepsPerSec);

    _leftMotor->setTargetSpeed(leftSpeedStepsPerSec);
    _rightMotor->setTargetSpeed(-rightSpeedStepsPerSec);
}

float RollingBasis::_wrapToPi(float ang) const
{
    ang = fmodf(ang + PI, 2.0f * PI);
    if (ang < 0.0f)
    {
        ang += 2.0f * PI;
    }
    return ang - PI;
}

bool RollingBasis::isMoving() const
{
    return _leftMotor->isMoving() || _rightMotor->isMoving();
}

void RollingBasis::stop()
{
    _cmdLinSpeed = _cmdAngSpeed = 0;
    _cmdPosition = _currentPosition;
    _leftMotor->setTargetSpeed(0);
    _rightMotor->setTargetSpeed(0);
    _linDistPid.reset();
    _angDistPid.reset();
    _moving = false;
    Serial.println("RollingBasis stopped.");
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
