#include "relative_forward.h"

#include <math.h>

RelativeForward::RelativeForward(Navigation* nav, double distance)
    : _navigation(nav), _distance(distance * DISTANCE_CALIBRATION) {
    Serial.printf("[RelativeForward] distance=%.1f mm calibrated from %.1f\n",
                  _distance, distance);
}

void RelativeForward::start() {
    _started = true;
    _finished = false;
    _startMs = millis();
    _lastPrintMs = 0;

    Point cur = _navigation->getPose();
    _target = cur;
    _target.x += _distance * cosf(cur.theta);
    _target.y += _distance * sinf(cur.theta);

    Serial.printf("[RelativeForward] Start to (%.1f, %.1f, %.3f)\n", _target.x,
                  _target.y, _target.theta);
    _navigation->setCommand(_target);
}

void RelativeForward::update() {
    if (!_started || _finished) {
        return;
    }

    _navigation->update();

    if (millis() - _startMs > _timeoutMs) {
        Serial.println("[RelativeForward] Timeout");
        stop();
        return;
    }

    Point cur = _navigation->getPose();
    float dist = Point::distance(cur, _target);

    if (millis() - _lastPrintMs > 1000) {
        Serial.printf("[RelativeForward] dist=%.1f mm moving=%d\n", dist,
                      _navigation->isMoving());
        _lastPrintMs = millis();
    }

    if (dist <= _arriveTolMm || !_navigation->isMoving()) {
        _finished = true;
        Serial.println("[RelativeForward] Finished");
    }
}

void RelativeForward::stop() {
    if (_started && !_finished) {
        _navigation->stop();
    }
    _finished = true;
}

bool RelativeForward::isFinished() const {
    return _finished;
}

const char* RelativeForward::name() const {
    return "RelativeForward";
}
