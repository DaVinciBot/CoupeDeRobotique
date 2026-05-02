#include "actionneur.h"

Actionneur::Actionneur(uint8_t pin) : _pin(pin) {
    pinMode(_pin, OUTPUT);
    _currentAngle = 0;
    _targetAngle = 0;
    _finished = true;
    Serial.printf("[Actionneur] pin %u initialized\n", _pin);
}

void Actionneur::start() {
    Serial.printf("[Actionneur] Start to %u deg\n", _targetAngle);
    _finished = false;
    _startMs = millis();
}

void Actionneur::update() {
    if (_finished) {
        return;
    }

    if (millis() - _startMs > _timeoutMs) {
        Serial.println("[Actionneur] Timeout");
        _finished = true;
        return;
    }

    if (_currentAngle < _targetAngle) {
        _currentAngle++;
    } else if (_currentAngle > _targetAngle) {
        _currentAngle--;
    } else {
        _finished = true;
        return;
    }

    uint16_t pwm = 1000 + (_currentAngle * 1000 / 180);
    digitalWrite(_pin, HIGH);
    delayMicroseconds(pwm);
    digitalWrite(_pin, LOW);
}

void Actionneur::stop() {
    _finished = true;
}

void Actionneur::setAngle(uint16_t angle) {
    _targetAngle = constrain(angle, 0, 180);
    Serial.printf("[Actionneur] target=%u deg\n", _targetAngle);
}

uint16_t Actionneur::getAngle() const {
    return _currentAngle;
}

bool Actionneur::isFinished() const {
    return _finished;
}

const char* Actionneur::name() const {
    return "Actionneur";
}
