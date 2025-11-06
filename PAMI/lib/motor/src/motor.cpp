#include "motor.h"

Motor::Motor(byte stepPin,
             byte dirPin,
             byte enablePin,
             unsigned int stepsPerRevolution,
             bool invertDirection)
    : _stepPin(stepPin),
      _dirPin(dirPin),
      _enablePin(enablePin),
      //_factorK(k),
      _invertDirection(invertDirection) {
    _stepsPerRevolution =
        stepsPerRevolution ;
    _targetSpeedStepsPerSec = 0.0f;
    _currentSpeedStepsPerSec = 0.0f;
    _acceleration = 0.0f;
    _moving = false;

    _lastStepTime = 0;
    _usDelayBetweenKSteps = 0.0f;
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
}

void Motor::setTargetSpeed(float stepsPerSec) {
    if (_invertDirection) {
        stepsPerSec = -stepsPerSec;
        Serial.println("inv ok");
    }
    _targetSpeedStepsPerSec = stepsPerSec * 1000.0f;
    _moving = (fabs(_targetSpeedStepsPerSec) >= 1.0f);
    enableMotor(_moving);
    //Serial.print("_targetSpeedStepsPerSec = ");
    //Serial.println(_targetSpeedStepsPerSec);
}

void Motor::setAcceleration(float stepsPerSec2) {
    _acceleration = max(0.0f, stepsPerSec2 * 100.0f);
}

void Motor::_setDirection(bool clockwise) {
    if (_dirPin == 0 || _dirPin == -1)
        return;  // No enable pin, do nothing
    digitalWrite(_dirPin, clockwise ? HIGH : LOW);
}

void Motor::doOneSteps() {
    //Serial.println("on appel one step");
    digitalWrite(_stepPin, HIGH);
    delayMicroseconds(500);
    digitalWrite(_stepPin, LOW);
    delayMicroseconds(500);
    

    if (_currentSpeedStepsPerSec >= 0 && !_invertDirection ||
        _currentSpeedStepsPerSec < 0 && _invertDirection) {
        _stepCount++;
    } else {
        _stepCount--;
    }
}

void Motor::update() {
    if (!_moving){
        Serial.println("Ca bouge pas !");    
        return;
    }
        
    //Serial.println("Ca bouge !");   
    unsigned long now = micros();
    unsigned long dt = now - _lastStepTime;
    float dtSec = dt * 1e-6f;
    float speedDiff = _acceleration * dtSec;
    //Serial.println(speedDiff);

    if (fabs(_currentSpeedStepsPerSec - _targetSpeedStepsPerSec) < speedDiff) {
        _currentSpeedStepsPerSec = _targetSpeedStepsPerSec;
    } else if (_currentSpeedStepsPerSec < _targetSpeedStepsPerSec) {
        _currentSpeedStepsPerSec += speedDiff;
    } else if (_currentSpeedStepsPerSec > _targetSpeedStepsPerSec) {
        _currentSpeedStepsPerSec -= speedDiff;
    }
    //Serial.print("_currentSpeedStepsPerSec =");
    //Serial.println(_currentSpeedStepsPerSec);

    if (fabs(_currentSpeedStepsPerSec) < 1.0f) {
        _usDelayBetweenKSteps = 1e6f;
    } else {
        _usDelayBetweenKSteps =
            (1e6f) / fabs(_currentSpeedStepsPerSec);
    }

    bool clockwise = (_currentSpeedStepsPerSec >= 0);
    _setDirection(clockwise);

    //Serial.print("dt = ");
    //Serial.print(dt);
    //Serial.print(", _usDelayBetweenKSteps = ");
    //Serial.println(_usDelayBetweenKSteps);

    if (dt >= _usDelayBetweenKSteps) {
        doOneSteps();
        //Serial.println("step !");
        
    }

    if (fabs(_targetSpeedStepsPerSec) < 1.0f &&
        fabs(_currentSpeedStepsPerSec) < 1.0f) {
        _moving = false;
        enableMotor(false);
    }
    _lastStepTime = now;
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
