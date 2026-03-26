#include "motor.h"

Motor::Motor(byte stepPin,
             byte dirPin,
             byte enablePin,
             unsigned int stepsPerRevolution,
             unsigned int pulse_us,
             bool invertDirection)
    : _stepPin(stepPin),
      _dirPin(dirPin),
      _enablePin(enablePin),
          _pulse_us(pulse_us),
      _stepsPerRevolution(stepsPerRevolution),
      _invertDirection(invertDirection) {
    _targetSpeedStepsPerSec = 0.0f;
    _currentSpeedStepsPerSec = 0.0f;
    _acceleration = 0.0f;
    _moving = false;

    _lastUpdateTime = micros();
    _lastStepTime = 0;
    _usDelayBetweenStep = 0.0f;
    _stepCount = 0;
}

void Motor::init() {
    pinMode(_stepPin, OUTPUT);
    pinMode(_dirPin, OUTPUT);
    pinMode(_enablePin, OUTPUT);
    enableMotor(false);
}

void Motor::enableMotor(bool enable) {
    digitalWrite(_enablePin, enable ? LOW : HIGH);
    _lastUpdateTime = micros();
}

void Motor::setTargetSpeed(float stepsPerSec) {
    if (_invertDirection) {
        stepsPerSec = -stepsPerSec;
    }
    _targetSpeedStepsPerSec = stepsPerSec * 1000.0f;
    _moving = (fabsf(_targetSpeedStepsPerSec) >= 1.0f);  // pose pb
    enableMotor(_moving);
    // Serial.print("_targetSpeedStepsPerSec = ");
    // Serial.println(_targetSpeedStepsPerSec);
}

void Motor::setAcceleration(float stepsPerSec2) {
    _acceleration = max(0.0f, stepsPerSec2 * 100.0f);
}

void Motor::_setDirection(bool clockwise) {
    if (_dirPin == 0 || _dirPin == -1)
        return;  // No enable pin, do nothing
    digitalWrite(_dirPin, clockwise ? HIGH : LOW);
}

void Motor::_doOneStep() {
    // Serial.println("Doing one step");
    digitalWrite(_stepPin, HIGH);
    delayMicroseconds(_pulse_us);
    digitalWrite(_stepPin, LOW);
    delayMicroseconds(_pulse_us);
    _lastStepTime = micros();

    if (_currentSpeedStepsPerSec >= 0 && !_invertDirection ||
        _currentSpeedStepsPerSec < 0 && _invertDirection) {
        _stepCount++;
    } else {
        _stepCount--;
    }
}

void Motor::update() {
    if (!_moving) {
        Serial.println("Motor not moving");
        
        return;
    }
    

    // Serial.println("Motor is moving");
    unsigned long now = micros();
    unsigned long dt = now - _lastUpdateTime;
    float dtSec = dt * 1e-6f;
    float speedDiff = _acceleration * dtSec;
    // Serial.println(speedDiff); 

    if (fabsf(_currentSpeedStepsPerSec - _targetSpeedStepsPerSec) < speedDiff) {
        _currentSpeedStepsPerSec = _targetSpeedStepsPerSec;
    } else if (_currentSpeedStepsPerSec < _targetSpeedStepsPerSec) {
        _currentSpeedStepsPerSec += speedDiff;
    } else if (_currentSpeedStepsPerSec > _targetSpeedStepsPerSec) {
        _currentSpeedStepsPerSec -= speedDiff;
    }
    // Serial.print("_currentSpeedStepsPerSec =");
    // Serial.println(_currentSpeedStepsPerSec);

    if (fabsf(_currentSpeedStepsPerSec) < 1.0f) {
        _usDelayBetweenStep = 1e6f;
    } else {
        _usDelayBetweenStep = (1e6f) / fabsf(_currentSpeedStepsPerSec);
    }

    bool clockwise = (_currentSpeedStepsPerSec >= 0);
    _setDirection(clockwise);

    // Serial.print("dt = ");
    // Serial.print(dt);
    // Serial.print(", _usDelayBetweenStep = ");
    // Serial.println(_usDelayBetweenStep);

    if (now - _lastStepTime >= _usDelayBetweenStep) {
        _doOneStep();
    }

    if (fabsf(_targetSpeedStepsPerSec) < 1.0f &&
        fabsf(_currentSpeedStepsPerSec) < 1.0f) {
        _moving = false;
        enableMotor(false);
    }

    _lastUpdateTime = now;
    
}

bool Motor::isMoving() const {
    return _moving;
}
 
unsigned int Motor::getStepsPerRev() const {
    return _stepsPerRevolution;
}

long Motor::getStepCount() const {
    return _stepCount;
}

void Motor::resetStepCount() {
    _stepCount = 0;
}
