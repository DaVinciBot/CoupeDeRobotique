#include "relative_turning.h"

#include <math.h>

RelativeTurning::RelativeTurning(Navigation* nav, double angle)
    : _navigation(nav), _angle(angle) {
    Serial.printf("[RelativeTurning] angle=%.3f rad\n", _angle);
}

void RelativeTurning::start() {
    _started = true;
    _finished = false;
    _startMs = millis();
    _lastPrintMs = 0;

    Point cur = _navigation->getPose();
    _target = cur;
    _target.theta = cur.theta + _angle;

    Serial.printf("[RelativeTurning] Start to %.3f rad\n", _target.theta);
    _navigation->setCommand(_target);
}

float RelativeTurning::angleErrorRad() const {
    Point cur = _navigation->getPose();
    float angleDiff = _target.theta - cur.theta;

    while (angleDiff > PI)
        angleDiff -= 2.0f * PI;
    while (angleDiff < -PI)
        angleDiff += 2.0f * PI;

    return angleDiff;
}

void RelativeTurning::update() {
    if (!_started || _finished) {
        return;
    }

    _navigation->update();

    if (millis() - _startMs > _timeoutMs) {
        Serial.println("[RelativeTurning] Timeout");
        stop();
        return;
    }

    float angleDiff = angleErrorRad();

    if (millis() - _lastPrintMs > 1000) {
        Serial.printf("[RelativeTurning] angle error=%.3f rad moving=%d\n",
                      angleDiff, _navigation->isMoving());
        _lastPrintMs = millis();
    }

    if (fabsf(angleDiff) <= _arriveTolRad || !_navigation->isMoving()) {
        _finished = true;
        Serial.println("[RelativeTurning] Finished");
    }
}

void RelativeTurning::stop() {
    if (_started && !_finished) {
        _navigation->stop();
    }
    _finished = true;
}

bool RelativeTurning::isFinished() const {
    return _finished;
}

const char* RelativeTurning::name() const {
    return "RelativeTurning";
}
