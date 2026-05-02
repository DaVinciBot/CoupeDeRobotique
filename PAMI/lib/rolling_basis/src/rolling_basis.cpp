#include "rolling_basis.h"

#include <math.h>

#include "../../../include/config.h"

#define POSITION_TOLERANCE_MM 1.0f
#define ANGLE_TOLERANCE_RAD 0.01f

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
      _linearSpeed(MAX_LINEAR_SPEED_MM_PER_S),
      _angularSpeed(MAX_ANGULAR_SPEED_RAD_PER_S),
      _phase(Phase::Idle),
      _rotateDuration(0.0f),
      _forwardDuration(0.0f),
      _rotateDirection(1.0f),
      _targetDTheta(0.0f),
      _targetDistanceMm(0.0f),
      _phaseStartLeftSteps(0),
      _phaseStartRightSteps(0),
      _startTime(micros()) {
    _leftMotor->init();
    _rightMotor->init();
    _leftMotor->resetStepCount();
    _rightMotor->resetStepCount();
    _leftMotor->setAcceleration(MOTOR_ACCELERATION_STEPS_PER_S2);
    _rightMotor->setAcceleration(MOTOR_ACCELERATION_STEPS_PER_S2);
}

void RollingBasis::setCommand(const Point& target) {
    Serial.printf(
        "[RB:setCommand] target=(%.1f, %.1f, %.3f) current=(%.1f, %.1f, "
        "%.3f)\n",
        target.x, target.y, target.theta, _currentPose.x, _currentPose.y,
        _currentPose.theta);

    _linearSpeed = MAX_LINEAR_SPEED_MM_PER_S;
    _angularSpeed = MAX_ANGULAR_SPEED_RAD_PER_S;

    float dx = target.x - _currentPose.x;
    float dy = target.y - _currentPose.y;
    float distance = sqrtf(dx * dx + dy * dy);
    float desiredTheta =
        (distance < POSITION_TOLERANCE_MM) ? target.theta : atan2f(dy, dx);
    float dTheta = _wrapToPi(desiredTheta - _currentPose.theta);

    _targetDTheta = dTheta * ANGULAR_CALIBRATION_FACTOR;
    _targetDistanceMm = distance;
    _rotateDuration = fabsf(_targetDTheta) / _angularSpeed;
    _rotateDirection = (_targetDTheta >= 0.0f) ? 1.0f : -1.0f;
    _forwardDuration =
        (distance < POSITION_TOLERANCE_MM) ? 0.0f : distance / _linearSpeed;

    _startTime = micros();
    _phaseStartLeftSteps = _leftMotor->getStepCount();
    _phaseStartRightSteps = _rightMotor->getStepCount();
    if (_rotateDuration > 0.0f) {
        _phase = Phase::Rotating;
    } else if (_forwardDuration > 0.0f) {
        _phase = Phase::Forwarding;
    } else {
        _phase = Phase::Done;
        _currentPose.theta = _wrapToPi(target.theta);
    }

    Serial.printf("[RB:setCommand] rotate=%.3fs forward=%.3fs phase=%d\n",
                  _rotateDuration, _forwardDuration, static_cast<int>(_phase));
}

void RollingBasis::update() {
    if (_phase == Phase::Idle || _phase == Phase::Done) {
        return;
    }

    unsigned long now = micros();

    if (_phase == Phase::Rotating) {
        float remaining =
            fabsf(_targetDTheta) - fabsf(_phaseAngularTravelRad());
        if (remaining > ANGLE_TOLERANCE_RAD) {
            _sendWheelSpeeds(0.0f, _angularSpeed * _rotateDirection);
            return;
        }

        _leftMotor->setTargetSpeed(0.0f);
        _rightMotor->setTargetSpeed(0.0f);
        _currentPose.theta = _wrapToPi(_currentPose.theta + _targetDTheta);
        _startTime = now;
        _phaseStartLeftSteps = _leftMotor->getStepCount();
        _phaseStartRightSteps = _rightMotor->getStepCount();

        if (_forwardDuration > 0.0f) {
            _phase = Phase::Forwarding;
            Serial.println("[RB] Rotation done -> Forwarding phase");
        } else {
            _phase = Phase::Done;
            Serial.println("[RB] Rotation done -> DONE phase");
        }
        return;
    }

    if (_phase == Phase::Forwarding) {
        float remaining =
            fabsf(_targetDistanceMm) - fabsf(_phaseLinearTravelMm());
        if (remaining > POSITION_TOLERANCE_MM) {
            _sendWheelSpeeds(_linearSpeed, 0.0f);
            return;
        }

        _leftMotor->setTargetSpeed(0.0f);
        _rightMotor->setTargetSpeed(0.0f);

        _currentPose.x += _targetDistanceMm * cosf(_currentPose.theta);
        _currentPose.y += _targetDistanceMm * sinf(_currentPose.theta);

        _phase = Phase::Done;
        Serial.println("[RB] Forwarding done -> DONE phase");
    }
}

float RollingBasis::_wrapToPi(float ang) const {
    ang = fmodf(ang + PI, 2.0f * PI);
    if (ang < 0.0f) {
        ang += 2.0f * PI;
    }
    return ang - PI;
}

void RollingBasis::_sendWheelSpeeds(float v, float w) {
    float halfBaseMm = _wheelBaseMm * 0.5f;
    float leftMmPerSec = v - w * halfBaseMm;
    float rightMmPerSec = v + w * halfBaseMm;
    float circumference = PI * _wheelDiameterMm;
    float leftStepsPerSec =
        leftMmPerSec * _leftMotor->getStepsPerRev() / circumference;
    float rightStepsPerSec =
        rightMmPerSec * _rightMotor->getStepsPerRev() / circumference;

    _leftMotor->setTargetSpeed(-leftStepsPerSec);
    _rightMotor->setTargetSpeed(-rightStepsPerSec);
}

float RollingBasis::_stepsToWheelDistanceMm(long steps,
                                            const Motor* motor) const {
    float circumference = PI * _wheelDiameterMm;
    return (static_cast<float>(steps) / motor->getStepsPerRev()) *
           circumference;
}

float RollingBasis::_phaseLinearTravelMm() const {
    float leftDistance = _stepsToWheelDistanceMm(
        _leftMotor->getStepCount() - _phaseStartLeftSteps, _leftMotor);
    float rightDistance = _stepsToWheelDistanceMm(
        _rightMotor->getStepCount() - _phaseStartRightSteps, _rightMotor);
    return -0.5f * (leftDistance + rightDistance);
}

float RollingBasis::_phaseAngularTravelRad() const {
    float leftDistance = _stepsToWheelDistanceMm(
        _leftMotor->getStepCount() - _phaseStartLeftSteps, _leftMotor);
    float rightDistance = _stepsToWheelDistanceMm(
        _rightMotor->getStepCount() - _phaseStartRightSteps, _rightMotor);
    return (leftDistance - rightDistance) / _wheelBaseMm;
}

bool RollingBasis::isMoving() const {
    bool phaseMoving =
        (_phase == Phase::Rotating || _phase == Phase::Forwarding);
    bool motorsMoving = _leftMotor->isMoving() || _rightMotor->isMoving();
    return phaseMoving || motorsMoving;
}

void RollingBasis::stop() {
    Serial.printf("[RB:stop] Phase %d -> IDLE\n", static_cast<int>(_phase));
    _leftMotor->setTargetSpeed(0.0f);
    _rightMotor->setTargetSpeed(0.0f);
    _phase = Phase::Idle;
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

void RollingBasis::moveForwardBlocking(float distanceMm) {
    Serial.printf("[Test] Blocking forward %.1f mm\n", distanceMm);

    _leftMotor->setAcceleration(MOTOR_ACCELERATION_STEPS_PER_S2);
    _rightMotor->setAcceleration(MOTOR_ACCELERATION_STEPS_PER_S2);

    _linearSpeed = MAX_LINEAR_SPEED_MM_PER_S;
    float duration = fabsf(distanceMm) / _linearSpeed;
    float dir = (distanceMm >= 0.0f) ? 1.0f : -1.0f;
    unsigned long start = micros();

    _sendWheelSpeeds(_linearSpeed * dir, 0.0f);

    while ((micros() - start) * 1e-6f < duration) {
        _leftMotor->update();
        _rightMotor->update();
    }

    _leftMotor->setTargetSpeed(0.0f);
    _rightMotor->setTargetSpeed(0.0f);

    unsigned long stopTime = millis();
    while (millis() - stopTime < 1000) {
        _leftMotor->update();
        _rightMotor->update();
    }

    _currentPose.x += distanceMm * cosf(_currentPose.theta);
    _currentPose.y += distanceMm * sinf(_currentPose.theta);
    Serial.println("[Test] Blocking forward done");
}

void RollingBasis::moveForwardStepsBlocking(long steps) {
    Serial.printf("[Test] Blocking forward %ld steps\n", steps);

    long targetSteps = labs(steps);
    if (targetSteps == 0) {
        return;
    }

    float dir = (steps >= 0) ? 1.0f : -1.0f;
    float circumference = PI * _wheelDiameterMm;
    float stepsPerSec = MAX_LINEAR_SPEED_MM_PER_S *
                        _leftMotor->getStepsPerRev() / circumference;
    unsigned long periodUs =
        static_cast<unsigned long>(1000000.0f / max(1.0f, stepsPerSec));

    for (long i = 0; i < targetSteps; ++i) {
        unsigned long startUs = micros();

        _leftMotor->stepOnceAtSignedSpeed(-dir);
        _rightMotor->stepOnceAtSignedSpeed(dir);

        unsigned long elapsedUs = micros() - startUs;
        if (elapsedUs < periodUs) {
            delayMicroseconds(periodUs - elapsedUs);
        }
    }

    _leftMotor->stopManualStepping();
    _rightMotor->stopManualStepping();

    Serial.printf("[Test] Blocking forward steps done: left=%ld right=%ld\n",
                  _leftMotor->getStepCount(), _rightMotor->getStepCount());
}

void RollingBasis::turnBlocking(float angleRad) {
    Serial.printf("[Test] Blocking turn %.3f rad\n", angleRad);

    _leftMotor->setAcceleration(MOTOR_ACCELERATION_STEPS_PER_S2);
    _rightMotor->setAcceleration(MOTOR_ACCELERATION_STEPS_PER_S2);

    _angularSpeed = MAX_ANGULAR_SPEED_RAD_PER_S;
    float targetDTheta = angleRad * ANGULAR_CALIBRATION_FACTOR;
    float duration = fabsf(targetDTheta) / _angularSpeed;
    float dir = (targetDTheta >= 0.0f) ? 1.0f : -1.0f;
    unsigned long start = micros();

    _sendWheelSpeeds(0.0f, _angularSpeed * dir);

    while ((micros() - start) * 1e-6f < duration) {
        _leftMotor->update();
        _rightMotor->update();
    }

    _leftMotor->setTargetSpeed(0.0f);
    _rightMotor->setTargetSpeed(0.0f);

    unsigned long stopTime = millis();
    while (millis() - stopTime < 1000) {
        _leftMotor->update();
        _rightMotor->update();
    }

    _currentPose.theta = _wrapToPi(_currentPose.theta + targetDTheta);
    Serial.println("[Test] Blocking turn done");
}
