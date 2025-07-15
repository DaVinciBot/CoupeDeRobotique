#include "navigation.h"

Navigation::Navigation(RollingBasis* basis, uint32_t timeoutMs)
    : _basis(basis),
      _sendIntervalMs(timeoutMs / DEFAULT_SEGMENTS),
      _timeoutMs(timeoutMs),
      _lastSendMs(0),
      _startMs(0),
      _lastTarget{0, 0, 0} {}

void Navigation::setCommand(const Point& targetPos) {
    _lastTarget = targetPos;
    _startMs = millis();
    _lastSendMs = 0;

    _waypoints.clear();
    Point start = _basis->getPose();
    for (size_t i = 1; i <= DEFAULT_SEGMENTS; ++i) {
        float t = float(i) / DEFAULT_SEGMENTS;
        Point wp;
        wp.x = start.x + t * (targetPos.x - start.x);
        wp.y = start.y + t * (targetPos.y - start.y);
        wp.theta = start.theta + Point::angle(start, targetPos);
        _waypoints.push_back(wp);
    }
    _wpIndex = 0;
    _basis->setCommand(_waypoints[_wpIndex]);
}

void Navigation::update() {
    uint32_t now = millis();

    // force stop after timeout
    if (_startMs && now - _startMs >= _timeoutMs) {
        stop();
        return;
    }

    // resend every interval
    if (_lastSendMs == 0 || now - _lastSendMs >= _sendIntervalMs) {
        if (_wpIndex >= _waypoints.size()) {
            Serial.println("[Navigation] No more waypoints to send.");
            return;  // no more waypoints to send
        }
        if (_wpIndex + 1 < _waypoints.size()) {
            _basis->setCommand(_waypoints[++_wpIndex]);
        }
        // else {
        //     stop(); // fin de la séquence
        // }
        _lastSendMs = now;
        Serial.print("[Navigation] Sending command to basis: ");
        Serial.print(_waypoints[_wpIndex].x);
        Serial.print(", ");
        Serial.print(_waypoints[_wpIndex].y);
        Serial.print(", ");
        Serial.print(_waypoints[_wpIndex].theta);
        Serial.println();
    }

    _basis->update();
}

bool Navigation::isMoving() const {
    return _basis->isMoving();
}

void Navigation::stop() {
    _basis->stop();
    _startMs = 0;
}

Point Navigation::getPose() const {
    return _basis->getPose();
}

float Navigation::getMeasuredLinearSpeed() const {
    return _basis->getLinearSpeedMmPerS();
}

float Navigation::getMeasuredAngularSpeed() const {
    return _basis->getAngularSpeedRadPerS();
}
