#include "Action.h"
#include "../../sensors/include/lidar_pami.h"

// GoToShopAction.h - example composite action (squelette)
#pragma once

#include "Action.h"

// forward declarations to avoid heavy includes
class RollingBasis;
class Navigation;
class Motor;

namespace actions {

class GoToShopAction : public Action {
public:
  GoToShopAction(RollingBasis* rb, Navigation* nav, Motor* left, Motor* right, lidar_pami* lidar = nullptr);
  ~GoToShopAction() override = default;

  void start() override;
  void update() override;
  void stop() override;
  bool isFinished() const override;
  const char* name() const override { return "GoToShop"; }

private:
  RollingBasis* _rb;
  Navigation* _nav;
  Motor* _left;
  Motor* _right;
  lidar_pami* _lidar;
  bool _finished;
  unsigned long _startedAt;
};

} // namespace actions
