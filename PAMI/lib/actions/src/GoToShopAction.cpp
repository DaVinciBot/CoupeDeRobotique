#include "actions/GoToShopAction.h"
#include <Arduino.h>

using namespace actions;

GoToShopAction::GoToShopAction(RollingBasis* rb, Navigation* nav, Motor* left, Motor* right, lidar_pami* lidar)
  : _rb(rb), _nav(nav), _left(left), _right(right), _lidar(lidar), _finished(false), _startedAt(0) {}

void GoToShopAction::start() {
  _startedAt = millis();
  _finished = false;
  Serial.println("GoToShopAction: start (squelette)");
  // Here: build a navigation target, call _nav->setCommand(...) or similar
}

void GoToShopAction::update() {
  // Example: poll LIDAR and log obstacle detection; real logic should
  // integrate navigation/rolling basis and handle obstacle avoidance.
  if (_lidar) {
    _lidar->update();
    if (_lidar->obstacleAhead(150)) {
      Serial.println("GoToShopAction: obstacle detected by LIDAR (150mm)");
      // real action could pause/navigation reroute here
    }
  }

  // Minimal skeleton finish after 2s for demo purposes
  if (!_finished && (millis() - _startedAt) > 2000) {
    Serial.println("GoToShopAction: reached target (simulated)");
    _finished = true;
  }
}

void GoToShopAction::stop() {
  Serial.println("GoToShopAction: stop (cleanup)");
  // abort navigation, stop motors, etc.
}

bool GoToShopAction::isFinished() const { return _finished; }
