#include "blocking_turn.h"

lidar_pami* BlockingTurn::_sLidar = nullptr;
uint16_t BlockingTurn::_sAcsDistance = 75;

BlockingTurn::BlockingTurn(RollingBasis* rb, float angleRad,
                           lidar_pami* lidar, uint16_t acsDistanceMm)
    : _rb(rb), _angleRad(angleRad) {
    _sLidar = lidar;
    _sAcsDistance = acsDistanceMm;
}

bool BlockingTurn::shouldPause() {
    if (_sLidar == nullptr) return false;
    _sLidar->update();
    bool paused = _sLidar->obstacleDirectlyAhead(_sAcsDistance);
    if (paused) {
        Serial.println("[ACS] Obstacle - pause turn");
    }
    return paused;
}

void BlockingTurn::start() {
    _started = true;
    _finished = false;
    _rb->turnBlocking(_angleRad, _sLidar ? shouldPause : nullptr);
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
