#include "actionneur.h"

Actionneur::Actionneur(uint8_t pin) : _pin(pin) {
    pinMode(_pin, OUTPUT);
    _currentAngle = 0;
    _targetAngle = 0;
    _finished = true;
    Serial.printf("Actionneur: pin %d initialized\n", _pin);
}

void Actionneur::start() {
    Serial.printf("Actionneur started, moving to %d°\n", _targetAngle);
    _finished = false;
    _startMs = millis();
}

void Actionneur::update() {
    if (_finished) {
        return;
    }

    // timeout check
    if (millis() - _startMs > _timeoutMs) {
        Serial.println("Actionneur: timeout, stopping");
        _finished = true;
        return;
    }

    if (_currentAngle < _targetAngle) {
        _currentAngle++;
    } else if (_currentAngle > _targetAngle) {
        _currentAngle--;
    } else {
        _finished = true;  // Angle atteint
    }
    uint16_t pwm = 1000 + (_currentAngle * 1000 / 180);
    digitalWrite(_pin, HIGH);
    delayMicroseconds(pwm);
    digitalWrite(_pin, LOW);
}

void Actionneur::stop() {
    Serial.println("Actionneur stopped");
    _finished = true;
}

void Actionneur::setAngle(uint16_t angle) {
    _targetAngle = angle;
    Serial.printf("Actionneur: target angle set to %d°\n", _targetAngle);
}

bool Actionneur::isFinished() const {
    return _finished;
}

const char* Actionneur::name() const {
    return "Actionneur";
}
