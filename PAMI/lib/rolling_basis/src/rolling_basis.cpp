#include "rolling_basis.h"
#include <math.h>

#define POSITION_TOLERANCE_MM 1.0f  // 1 mm
#define ANGLE_TOLERANCE_RAD 0.01f   // env. 0.57°

RollingBasis::RollingBasis(Motor* leftMotor,
                           Motor* rightMotor,
                           float wheelDiameterMm,
                           float wheelBaseMm,
                           const Point& initialPosition)
    : _leftMotor(leftMotor),
      _rightMotor(rightMotor),
      _wheelDiameterMm(wheelDiameterMm),
      _wheelBaseMm(wheelBaseMm),
      _currentPose(initialPosition),
      _linearSpeed(20.0f),
      _angularSpeed(0.1f),
      _phase(Phase::Idle),
      _rotateDuration(0.0f),
      _forwardDuration(0.0f),
      _rotateDirection(1.0f),
      _startTime(std::chrono::steady_clock::now()) {
    _leftMotor->init();
    _rightMotor->init();
    _leftMotor->resetStepCount();
    _rightMotor->resetStepCount();
    _leftMotor->setAcceleration(200.0f * 3);
    _rightMotor->setAcceleration(200.0f);
}
// TODO: refactor this constructor pour pouvoir paramétrer la vitesse et l'accélération angulaire et linéaire dans le config BIEN PRECISER L'UNITE

void RollingBasis::setCommand(const Point& target) {
    float dx = target.x - _currentPose.x;
    float dy = target.y - _currentPose.y;
    float desiredTheta = atan2f(dy, dx);
    float dTheta = _wrapToPi(desiredTheta - _currentPose.theta);
    _rotateDuration = fabsf(dTheta) / _angularSpeed;
    _rotateDirection = (dTheta >= 0 ? +1.0f : -1.0f);

    // distance to travel
    float distance = sqrtf(dx * dx + dy * dy);
    _forwardDuration = distance / _linearSpeed;

    // timestamps
    _startTime = std::chrono::steady_clock::now();
    _phase = (_rotateDuration > 0 ? Phase::Rotating : Phase::Forwarding);

    // Serial.print("[Command] New target set: x=");
    // Serial.print(_cmdPosition.x);
    // Serial.print(" y=");
    // Serial.print(_cmdPosition.y);
    // Serial.print(" theta=");
    // Serial.print(_cmdPosition.theta);
    Serial.print("Rotate duration: ");
    Serial.print(_rotateDuration);
    Serial.print(" s, Forward duration: ");
    Serial.print(_forwardDuration);
    Serial.println(" s");
}

void RollingBasis::update() {
    using namespace std::chrono;
    if (_phase == Phase::Idle || _phase == Phase::Done)
        return;

    auto now = steady_clock::now();
    float elapsed = duration<float>(now - _startTime).count();

    if (_phase == Phase::Rotating) {
        if (elapsed < _rotateDuration) {
            float w = _angularSpeed * _rotateDirection;
            _sendWheelSpeeds(0.0f, w);
        } else {
            _startTime = now;
            _phase = Phase::Forwarding;
            Serial.print("Rotation done, switching to Forwarding phase. ");
        }
    }
    if (_phase == Phase::Forwarding) {
        if (elapsed < _forwardDuration) {
            _sendWheelSpeeds(_linearSpeed, 0.0f);
        } else {
            _leftMotor->setTargetSpeed(0);
            _rightMotor->setTargetSpeed(0);
            _phase = Phase::Done;
        }
    }

    // if (!_moving) {
    //     _cmdPosition = _currentPosition;
    //     return;
    // }

    // auto now = std::chrono::steady_clock::now();
    // float dt = std::chrono::duration<float>(now - _lastTime).count();
    // if (dt <= 0)
    //     return;

    // _computeOdometry(dt);

    // float distErr = Point::distance(_currentPosition, _cmdPosition);
    // float bearErr = _wrapToPi(_cmdPosition.theta - _currentPosition.theta);

    // // Serial.print("[Update] Error: dist=");
    // // Serial.print(distErr);
    // // Serial.print(" bear=");
    // // Serial.println(bearErr);

    // if (distErr < POSITION_TOLERANCE_MM && _wrapToPi(bearErr) <
    // ANGLE_TOLERANCE_RAD) {
    //     stop();
    //     return;
    // }

    // _applyControl(dt);

    _leftMotor->update();
    _rightMotor->update();
    // _lastTime = now;
}

// void RollingBasis::_computeOdometry(float dt)
// {
//     long leftSteps = _leftMotor->getStepCount();
//     long rightSteps = _rightMotor->getStepCount();
//     long dL = leftSteps - _prevLeftSteps;
//     long dR = rightSteps - _prevRightSteps;
//     _prevLeftSteps = leftSteps;
//     _prevRightSteps = rightSteps;

//     float mmPerStep = (M_PI * _wheelDiameterMm) /
//     _leftMotor->getStepsPerRev(); float dLeft = dL * mmPerStep; float dRight
//     = dR * mmPerStep;

//     float dCenter = 0.5f * (dLeft + dRight);
//     float dTheta = (dRight - dLeft) / _wheelBaseMm;

//     _currentPosition.x += dCenter * cosf(_currentPosition.theta + dTheta
//     / 2.0f); _currentPosition.y += dCenter * sinf(_currentPosition.theta +
//     dTheta / 2.0f); _currentPosition.theta = _wrapToPi(_currentPosition.theta
//     + dTheta);

//     _measLinSpeed = dCenter / dt;
//     _measAngSpeed = dTheta / dt;

//     // Serial.print("[Odometry] dLeft=");
//     // Serial.print(dLeft);
//     // Serial.print(" dRight=");
//     // Serial.print(dRight);
//     // Serial.print(" dTheta=");
//     // Serial.println(dTheta);

//     // Serial.print("[Odometry] New pose: x=");
//     // Serial.print(_currentPosition.x);
//     // Serial.print(" y=");
//     // Serial.print(_currentPosition.y);
//     // Serial.print(" theta=");
//     // Serial.println(_currentPosition.theta);
//     // Serial.print("[Odometry] Speeds: lin=");
//     // Serial.print(_measLinSpeed);
//     // Serial.print(" mm/s, ang=");
//     // Serial.print(_measAngSpeed);
//     // Serial.println(" rad/s");
// }

// void RollingBasis::_applyControl(float dt)
// {
//     _linDistPid.setSampleTime(dt);
//     _angDistPid.setSampleTime(dt);

//     float xerr = _cmdPosition.x - _currentPosition.x; // mm
//     float yerr = _cmdPosition.y - _currentPosition.y; // mm

//     float distErr = xerr * cosf(_currentPosition.theta) + yerr *
//     sinf(_currentPosition.theta); // mm
//     // double mag = sqrt(pow(xerr, 2) + pow(yerr, 2));
//     // double sign = (distErr >= 0.0) ? +1.0 : -1.0;
//     // distErr = mag * sign;

//     float bearErr = _wrapToPi(_cmdPosition.theta - _currentPosition.theta);
//     // rad

//     // Serial.print("[Control] distErr=");
//     // Serial.print(distErr);
//     // Serial.print(" bearErr=");
//     // Serial.println(bearErr);

//     float corrLinD = _linDistPid.compute(distErr); // mm/s
//     float corrAngD = _angDistPid.compute(bearErr); // rad/s

//     float spdLinRef = fmaxf(fminf(corrLinD, MAX_LINEAR_SPEED_MM_PER_S),
//     -MAX_LINEAR_SPEED_MM_PER_S); float spdAngRef = fmaxf(fminf(corrAngD,
//     MAX_ANGULAR_SPEED_RAD_PER_S), -MAX_ANGULAR_SPEED_RAD_PER_S);

//     float cmdLin = spdLinRef;
//     float cmdAng = spdAngRef;

//     // Serial.print("[Control] cmdLin=");
//     // Serial.print(cmdLin);
//     // Serial.print(" mm/s, cmdAng=");
//     // Serial.print(cmdAng);
//     // Serial.println(" rad/s");

//     float halfBaseMm = _wheelBaseMm * 0.5f;
//     float leftSpeedMmPerSec = cmdLin - cmdAng * halfBaseMm;
//     float rightSpeedMmPerSec = cmdLin + cmdAng * halfBaseMm;

//     float circumference = M_PI * _wheelDiameterMm;
//     float leftSpeedStepsPerSec = (leftSpeedMmPerSec / circumference) *
//     _leftMotor->getStepsPerRev(); float rightSpeedStepsPerSec =
//     (rightSpeedMmPerSec / circumference) * _rightMotor->getStepsPerRev();

//     // Serial.print("[Control] leftSpeedStepsPerSec=");
//     // Serial.print(leftSpeedStepsPerSec);
//     // Serial.print(" rightSpeedStepsPerSec=");
//     // Serial.println(rightSpeedStepsPerSec);

//     _leftMotor->setTargetSpeed(leftSpeedStepsPerSec);
//     _rightMotor->setTargetSpeed(rightSpeedStepsPerSec);
// }

float RollingBasis::_wrapToPi(float ang) const {
    ang = fmodf(ang + PI, 2.0f * PI);
    if (ang < 0.0f) {
        ang += 2.0f * PI;
    }
    return ang - PI;
}

void RollingBasis::_sendWheelSpeeds(float v, float w) {
    float halfBaseMm = _wheelBaseMm * 0.5f;
    float leftMm = v - w * halfBaseMm;
    float rightMm = v + w * halfBaseMm;
    float circumference = M_PI * _wheelDiameterMm;
    float leftSteps = leftMm / circumference * _leftMotor->getStepsPerRev();
    float rightSteps = rightMm / circumference * _rightMotor->getStepsPerRev();
    _leftMotor->setTargetSpeed(leftSteps * 8);
    _rightMotor->setTargetSpeed(rightSteps);
}

bool RollingBasis::isMoving() const {
    return _phase == Phase::Rotating || _phase == Phase::Forwarding;
    // return _leftMotor->isMoving() || _rightMotor->isMoving();
}

void RollingBasis::stop() {
    // _cmdLinSpeed = _cmdAngSpeed = 0;
    // _cmdPosition = _currentPosition;
    _leftMotor->setTargetSpeed(0);
    _rightMotor->setTargetSpeed(0);
    _phase = Phase::Idle;
    _linearSpeed = 0.0f;
    _angularSpeed = 0.0f;
    // _linDistPid.reset();
    // _angDistPid.reset();
    // _moving = false;
    Serial.println("RollingBasis stopped.");
}

Point RollingBasis::getPose() const {
    return _currentPose;
}

float RollingBasis::getLinearSpeedMmPerS() const {
    return _linearSpeed;
}
float RollingBasis::getAngularSpeedRadPerS() const {
    return _angularSpeed;
}
