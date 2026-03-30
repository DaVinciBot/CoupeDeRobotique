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
    _rightMotor->setAcceleration(200.0f);
}
// TODO: refactor this constructor pour pouvoir paramétrer la vitesse et
// l'accélération angulaire et linéaire dans le config BIEN PRECISER L'UNITE

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
    _startTime = micros();
    _phase = (_rotateDuration > 0 ? Phase::Rotating : Phase::Forwarding);

    // Serial.printf("[Command] New target set: x=%f, y=%f, theta=%f\n",
    // _cmdPosition.x, _cmdPosition.y, _cmdPosition.theta);
    Serial.printf("Rotate duration: %f s, Forward duration: %f s\n",
                  _rotateDuration, _forwardDuration);
}

void RollingBasis::update() {
    // Serial.printf("Phase: %s\n", phaseNames[(int)_phase]);

    if (_phase == Phase::Idle || _phase == Phase::Done) {
        return;
    }

    unsigned long now = micros();
    float elapsed = (now - _startTime) * 1e-6f;
    Serial.println(elapsed);

    if (_phase == Phase::Rotating) {
        if (elapsed < _rotateDuration) {
            float w = _angularSpeed * _rotateDirection;
            _sendWheelSpeeds(0.0f, w);
            Serial.println("Rotating...");
            Serial.print(w);
        } else {
            _phase = Phase::Forwarding;
            _startTime = now;
            elapsed = 0.0f;
            Serial.println("Rotation done, switching to Forwarding phase.");
        }
    }
    if (_phase == Phase::Forwarding) {
        if (elapsed < _forwardDuration) {
            _sendWheelSpeeds(_linearSpeed, 0.0f);
            Serial.println("Forwarding...");
        } else {
            _leftMotor->setTargetSpeed(0);
            _rightMotor->setTargetSpeed(0);
            _phase = Phase::Done;
            Serial.println("Forwarding done, switching to Done phase.");
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
    return _phase == Phase::Rotating || _phase == Phase::Forwarding;
}

void RollingBasis::stop() {
    _leftMotor->setTargetSpeed(0);
    _rightMotor->setTargetSpeed(0);
    _phase = Phase::Idle;
    _linearSpeed = 0.0f;
    _angularSpeed = 0.0f;
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
