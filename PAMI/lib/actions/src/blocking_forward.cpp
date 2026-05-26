#include "blocking_forward.h"

BlockingForward::BlockingForward(RollingBasis* rb, float distanceMm)
    : _rb(rb), _distanceMm(distanceMm) {}

bool BlockingForward::shouldPause() {
    return acsBlocked;
}

void BlockingForward::start() {
    _started = true;
    _finished = false;
    _rb->moveForwardBlocking(_distanceMm, shouldPause);
    _finished = true;
}

void BlockingForward::update() {}

void BlockingForward::stop() {
    if (_started && !_finished) {
        _rb->stop();
    }
    _finished = true;
}

bool BlockingForward::isFinished() const {
    return _finished;
}

const char* BlockingForward::name() const {
    return "BlockingForward";
}
