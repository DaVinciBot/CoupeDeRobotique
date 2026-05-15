#include "go_to.h"

namespace {
float wrapToPi(float angle) {
    angle = fmodf(angle + PI, 2.0f * PI);
    if (angle < 0.0f) {
        angle += 2.0f * PI;
    }
    return angle - PI;
}
}  // namespace

lidar_pami* GoTo::_sLidar = nullptr;
uint16_t GoTo::_sAcsDistance = 75;

GoTo::GoTo(RollingBasis* rb, const Point& target,
           lidar_pami* lidar, uint16_t acsDistanceMm)
    : _rb(rb), _target(target) {
    _sLidar = lidar;
    _sAcsDistance = acsDistanceMm;
    Serial.printf("[GoTo] Target set to x=%.1f y=%.1f theta=%.3f\n", _target.x,
                  _target.y, _target.theta);
}

bool GoTo::shouldPause() {
    if (_sLidar == nullptr) return false;
    _sLidar->update();
    bool paused = _sLidar->obstacleAhead(_sAcsDistance);
    if (paused) {
        Serial.println("[ACS] Obstacle - pause GoTo");
    }
    return paused;
}

void GoTo::start() {
    _started = true;
    _finished = false;
    RollingBasis::PauseCheckFn pause = _sLidar ? shouldPause : nullptr;

    Point cur = _rb->getPose();
    Serial.printf(
        "[GoTo] Start from (%.1f, %.1f, %.3f) to (%.1f, %.1f, %.3f)\n", cur.x,
        cur.y, cur.theta, _target.x, _target.y, _target.theta);

    float distance = Point::distance(cur, _target);
    if (distance > 0.0f) {
        float targetHeading = static_cast<float>(Point::angle(cur, _target));
        _rb->turnBlocking(wrapToPi(targetHeading - cur.theta), pause);
        _rb->moveForwardBlocking(distance, pause);
    }

    cur = _rb->getPose();
    _rb->turnBlocking(wrapToPi(_target.theta - cur.theta), pause);
    _rb->stop();
    _finished = true;
    Serial.println("[GoTo] Finished");
}

void GoTo::update() {}

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
