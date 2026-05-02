#include "relative_backward.h"

#include <math.h>

RelativeBackward::RelativeBackward(Navigation* nav, double distance)
    : _navigation(nav), _distance(distance) {
    Serial.printf("[RelativeBackward] distance=%.1f mm calibrated from %.1f\n",
                  _distance, distance);
}

void RelativeBackward::start() {
    _started = true;
    _finished = false;
    _startMs = millis();
    _lastPrintMs = 0;

    Point cur = _navigation->getPose();
    _target = cur;
    _target.x -= _distance * cosf(cur.theta);
    _target.y -= _distance * sinf(cur.theta);

    Serial.printf("[RelativeBackward] Start to (%.1f, %.1f, %.3f)\n", _target.x,
                  _target.y, _target.theta);
    _navigation->setCommand(_target);
}

void RelativeBackward::update() {
    if (!_started || _finished) {
        return;
    }

    _navigation->update();

    if (millis() - _startMs > _timeoutMs) {
        Serial.println("[RelativeBackward] Timeout");
        stop();
        return;
    }

    Point cur = _navigation->getPose();
    float dist = Point::distance(cur, _target);

    if (millis() - _lastPrintMs > 1000) {
        Serial.printf("[RelativeBackward] dist=%.1f mm moving=%d\n", dist,
                      _navigation->isMoving());
        _lastPrintMs = millis();
    }

    if (dist <= _arriveTolMm || !_navigation->isMoving()) {
        _finished = true;
        Serial.println("[RelativeBackward] Finished");
    }
}

void RelativeBackward::stop() {
    if (_started && !_finished) {
        _navigation->stop();
    }
    _finished = true;
}

bool RelativeBackward::isFinished() const {
    return _finished;
}

const char* RelativeBackward::name() const {
    return "RelativeBackward";
}
