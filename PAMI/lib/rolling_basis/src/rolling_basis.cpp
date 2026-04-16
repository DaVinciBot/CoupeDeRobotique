#include "rolling_basis.h"
#include <math.h>
#include "config.h"

#define ANGULAR_CALIBRATION_FACTOR 0.75f  // Robot tourne trop (~120° au lieu de 90°), donc on multiplie par 0.75
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
      _currentPose(initialPosition)
{
    _linearSpeed = 23.0f; //ne sert a rien a part pour déterminer le temps qu'il met pour avancer ?? dcp c un peu une valeur magique
    _angularSpeed = 1.38f; // encore une valeur magique pour faire tourner le robot a une vitesse raisonnable (environ 1.38 rad/s correspond a 80 deg/s)
    _phase = Phase::Idle;
    _rotateDuration = 0.0f;
    _forwardDuration = 0.0f;
    _rotateDirection = 1.0f;
    _startTime = micros();

    _leftMotor->init();
    _rightMotor->init();
    _leftMotor->resetStepCount();
    _rightMotor->resetStepCount();
    _leftMotor->setAcceleration(1000.0f);//avec 200, le moteur met 1s a aller a la meme vitesse que l'autre moteur jsp pourquoi mais ca fixe ca a 1000
    _rightMotor->setAcceleration(1000.0f);
}
// TODO: refactor this constructor pour pouvoir paramétrer la vitesse et
// l'accélération angulaire et linéaire dans le config BIEN PRECISER L'UNITE

void RollingBasis::setCommand(const Point& target) {
    Serial.printf("[RB:setCommand] NEW TARGET (%.1f, %.1f, %.3f) from current (%.1f, %.1f, %.3f)\n",
                  target.x, target.y, target.theta, _currentPose.x, _currentPose.y, _currentPose.theta);
    
    // Restaurer les vitesses si elles ont été réinitialisées par stop()
    if (_linearSpeed == 0.0f) {
        _linearSpeed = 23.0f;
    }
    if (_angularSpeed == 0.0f) {
        _angularSpeed = 1.38f;
    }
    
    float dx = target.x - _currentPose.x;
    float dy = target.y - _currentPose.y;
    float desiredTheta = atan2f(dy, dx);
    float dTheta = _wrapToPi(desiredTheta - _currentPose.theta);
    
    // Apply calibration: reduce the angle target to compensate for excessive actual rotation
    _targetDTheta = dTheta * ANGULAR_CALIBRATION_FACTOR;
    _rotateDuration = fabsf(_targetDTheta) / _angularSpeed;
    _rotateDirection = (_targetDTheta >= 0 ? +1.0f : -1.0f);

    // distance to travel
    float distance = sqrtf(dx * dx + dy * dy);
    _forwardDuration = distance / _linearSpeed;

    // timestamps
    _startTime = micros();
    _phase = (_rotateDuration > 0 ? Phase::Rotating : Phase::Forwarding);

    Serial.printf("[RB:setCommand] Rotate: %.3fs, Forward: %.3fs (speeds: lin=%.1f, ang=%.2f) -> Phase: %s\n",
                  _rotateDuration, _forwardDuration, _linearSpeed, _angularSpeed,
                  _phase == Phase::Rotating ? "ROTATING" : "FORWARDING");
}

void RollingBasis::update() {
    // Serial.printf("Phase: %s\n", phaseNames[(int)_phase]);

    if (_phase == Phase::Idle || _phase == Phase::Done) {
        Serial.printf("[RB:update] Phase is %s, returning\n", 
            _phase == Phase::Idle ? "IDLE" : "DONE");
        return;
    }

    unsigned long now = micros();
    float elapsed = (now - _startTime) * 1e-6f;

    if (_phase == Phase::Rotating) {
        if (elapsed < _rotateDuration) {
            float w = _angularSpeed * _rotateDirection;
            _sendWheelSpeeds(0.0f, w);
            //Serial.println("[RB] Rotating...");
        } else {
            _phase = Phase::Forwarding;
            _startTime = now;
            elapsed = 0.0f;
            // Update orientation after rotation - use _targetDTheta (calibrated angle)
            _currentPose.theta += _targetDTheta;
            Serial.println("[RB] Rotation done -> Forwarding phase");
        }
    }
    else if (_phase == Phase::Forwarding) {  // ← MUST BE else if, not if!
        if (elapsed < _forwardDuration) {
            _sendWheelSpeeds(_linearSpeed, 0.0f);
            //Serial.println("[RB] Forwarding...");
        } else {
            _leftMotor->setTargetSpeed(0);
            _rightMotor->setTargetSpeed(0);

            // Update position after forwarding
            float distance = _forwardDuration * _linearSpeed;
            _currentPose.x += distance * cosf(_currentPose.theta);
            _currentPose.y += distance * sinf(_currentPose.theta);

            _phase = Phase::Done;
            Serial.println("[RB] Forwarding done -> DONE phase");
        }
    }

    _leftMotor->update();
    _rightMotor->update();
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
    float leftMm = v - w * halfBaseMm;
    float rightMm = v + w * halfBaseMm;
    float circumference = M_PI * _wheelDiameterMm;
    float leftSteps = leftMm / circumference * _leftMotor->getStepsPerRev();
    float rightSteps = rightMm / circumference * _rightMotor->getStepsPerRev();
    // Serial.println(leftSteps);
    _leftMotor->setTargetSpeed(leftSteps);
    _rightMotor->setTargetSpeed(rightSteps);
}

bool RollingBasis::isMoving() const {
    bool moving = (_phase == Phase::Rotating || _phase == Phase::Forwarding);
    // Serial.printf("[RB:isMoving] Phase=%d -> %d\n", (int)_phase, moving);
    return moving;
}

void RollingBasis::stop() {
    Serial.printf("[RB:stop] Phase %d -> IDLE\n", (int)_phase);
    _leftMotor->setTargetSpeed(0);
    _rightMotor->setTargetSpeed(0);
    _phase = Phase::Idle;
    _linearSpeed = 0.0f;
    _angularSpeed = 0.0f;
    Serial.println("[RB:stop] RollingBasis STOPPED");
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
