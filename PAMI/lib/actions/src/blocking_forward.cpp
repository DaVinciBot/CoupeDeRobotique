#include "blocking_forward.h"

lidar_pami* BlockingForward::_sLidar = nullptr;
uint16_t BlockingForward::_sAcsDistance = 75;

BlockingForward::BlockingForward(RollingBasis* rb, float distanceMm,
                                 lidar_pami* lidar, uint16_t acsDistanceMm)
    : _rb(rb), _distanceMm(distanceMm) {
    _sLidar = lidar;
    _sAcsDistance = acsDistanceMm;
}

bool BlockingForward::shouldPause() {
    if (_sLidar == nullptr) return false;
    _sLidar->update();
    bool paused = _sLidar->obstacleAhead(_sAcsDistance);
    if (paused) {
        Serial.println("[ACS] Obstacle - pause");
    }
    return paused;
}

void BlockingForward::start() {
    _started = true;
    _finished = false;
    _rb->moveForwardBlocking(_distanceMm,
                             _sLidar ? shouldPause : nullptr);
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
