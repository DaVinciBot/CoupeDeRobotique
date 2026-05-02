#include "AtoB.h"

AtoB::AtoB(RollingBasis* rb, const Point& target) : _rb(rb), _target(target) {
    Serial.printf("[AtoB] Target set to x=%.1f y=%.1f theta=%.3f\n", _target.x,
                  _target.y, _target.theta);
}

void AtoB::start() {
    _started = true;
    _finished = false;
    _startMs = millis();
    _lastPrintMs = 0;

    Point cur = _rb->getPose();
    Serial.printf(
        "[AtoB] Start from (%.1f, %.1f, %.3f) to (%.1f, %.1f, %.3f)\n", cur.x,
        cur.y, cur.theta, _target.x, _target.y, _target.theta);

    _rb->setCommand(_target);
}

void AtoB::update() {
    if (!_started || _finished) {
        return;
    }

    _rb->update();

    if (millis() - _startMs > _timeoutMs) {
        Serial.println("[AtoB] Timeout");
        _rb->stop();
        _finished = true;
        return;
    }

    Point cur = _rb->getPose();
    float dist = Point::distance(cur, _target);

    if (millis() - _lastPrintMs > 1000) {
        Serial.printf("[AtoB] dist=%.1f mm moving=%d\n", dist, _rb->isMoving());
        _lastPrintMs = millis();
    }

    if (dist <= _arriveTolMm || !_rb->isMoving()) {
        Serial.printf("[AtoB] Finished dist=%.1f moving=%d\n", dist,
                      _rb->isMoving());
        _finished = true;
    }
}

void AtoB::stop() {
    if (_started && !_finished) {
        _rb->stop();
    }
    _finished = true;
}

bool AtoB::isFinished() const {
    return _finished;
}

const char* AtoB::name() const {
    return "AtoB";
}
