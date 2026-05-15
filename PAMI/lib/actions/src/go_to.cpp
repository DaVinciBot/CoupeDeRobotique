#include "go_to.h"

#include "../../../include/config.h"

namespace {
float wrapToPi(float angle) {
    angle = fmodf(angle + PI, 2.0f * PI);
    if (angle < 0.0f) {
        angle += 2.0f * PI;
    }
    return angle - PI;
}
}  // namespace

GoTo::GoTo(RollingBasis* rb, const Point& target)
    : _rb(rb), _target(target) {
    DEBUG_PRINTF("[GoTo] Target set to x=%.1f y=%.1f theta=%.3f\n", _target.x,
                  _target.y, _target.theta);
}

bool GoTo::shouldPause() {
    return acsBlocked;
}

void GoTo::start() {
    _started = true;
    _finished = false;

    Point cur = _rb->getPose();
    DEBUG_PRINTF(
        "[GoTo] Start from (%.1f, %.1f, %.3f) to (%.1f, %.1f, %.3f)\n", cur.x,
        cur.y, cur.theta, _target.x, _target.y, _target.theta);

    float distance = Point::distance(cur, _target);
    if (distance > 0.0f) {
        float targetHeading = static_cast<float>(Point::angle(cur, _target));
        _rb->turnBlocking(wrapToPi(targetHeading - cur.theta));
        _rb->moveForwardBlocking(distance, shouldPause);
    }

    cur = _rb->getPose();
    _rb->turnBlocking(wrapToPi(_target.theta - cur.theta));
    _rb->stop();
    _finished = true;
    DEBUG_PRINTLN("[GoTo] Finished");
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
