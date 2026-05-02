#include "go_to.h"

GoTo::GoTo(RollingBasis* rb, const Point& target) : _rb(rb), _target(target) {
    Serial.printf("[GoTo] Target set to x=%.1f y=%.1f theta=%.3f\n", _target.x,
                  _target.y, _target.theta);
}

void GoTo::start() {
    _started = true;
    _finished = false;
    _startMs = millis();
    _lastPrintMs = 0;

    Point cur = _rb->getPose();
    Serial.printf(
        "[GoTo] Start from (%.1f, %.1f, %.3f) to (%.1f, %.1f, %.3f)\n", cur.x,
        cur.y, cur.theta, _target.x, _target.y, _target.theta);

    _rb->setCommand(_target);
}

void GoTo::update() {
    if (!_started || _finished) {
        return;
    }

    _rb->update();

    if (millis() - _startMs > _timeoutMs) {
        Serial.println("[GoTo] Timeout");
        _rb->stop();
        _finished = true;
        return;
    }

    Point cur = _rb->getPose();
    float dist = Point::distance(cur, _target);

    if (millis() - _lastPrintMs > 1000) {
        Serial.printf("[GoTo] dist=%.1f mm moving=%d\n", dist, _rb->isMoving());
        _lastPrintMs = millis();
    }

    if (dist <= _arriveTolMm || !_rb->isMoving()) {
        Serial.printf("[GoTo] Finished dist=%.1f moving=%d\n", dist,
                      _rb->isMoving());
        _finished = true;
    }
}

void GoTo::stop() {
    if (_started && !_finished) {
        _rb->stop();
    }
    _finished = true;
}

bool GoTo::isFinished() const {
    return _finished;
}

const char* GoTo::name() const {
    return "GoTo";
}
