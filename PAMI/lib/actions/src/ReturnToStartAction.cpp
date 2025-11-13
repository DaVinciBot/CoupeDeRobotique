#include "actions/ReturnToStartAction.h"
#include <Arduino.h>

using namespace actions;

ReturnToStartAction::ReturnToStartAction(RollingBasis* rb, Navigation* nav, Motor* left, Motor* right, lidar_pami* lidar)
  : _rb(rb), _nav(nav), _left(left), _right(right), _lidar(lidar), _finished(false), _startedAt(0) {}

void ReturnToStartAction::start() {
  _startedAt = millis();
  _finished = false;
  Serial.println("ReturnToStartAction: start (squelette)");
  // Here: prepare navigation to origin
}

void ReturnToStartAction::update() {
  if (_lidar) {
    _lidar->update();
    if (_lidar->obstacleAhead(120)) {
      Serial.println("ReturnToStartAction: LIDAR reports obstacle (120mm)");
    }
  }

  if (!_finished && (millis() - _startedAt) > 1500) {
    Serial.println("ReturnToStartAction: reached origin (simulated)");
    _finished = true;
  }
}

void ReturnToStartAction::stop() {
  Serial.println("ReturnToStartAction: stop (cleanup)");
}

bool ReturnToStartAction::isFinished() const { return _finished; }
