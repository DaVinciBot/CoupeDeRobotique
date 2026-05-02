#include "blocking_turn.h"

BlockingTurn::BlockingTurn(RollingBasis* rb, float angleRad)
    : _rb(rb), _angleRad(angleRad) {}

void BlockingTurn::start() {
    _started = true;
    _finished = false;
    _rb->turnBlocking(_angleRad);
    _finished = true;
}

void BlockingTurn::update() {}

void BlockingTurn::stop() {
    if (_started && !_finished) {
        _rb->stop();
    }
    _finished = true;
}

bool BlockingTurn::isFinished() const {
    return _finished;
}

const char* BlockingTurn::name() const {
    return "BlockingTurn";
}
