// ReturnToStartAction.h - example action to return robot to start
#pragma once


#include "Action.h"
#include "../../sensors/include/lidar_pami.h"

class RollingBasis;
class Navigation;
class Motor;

namespace actions {

class ReturnToStartAction : public Action {
public:
  ReturnToStartAction(RollingBasis* rb, Navigation* nav, Motor* left, Motor* right, lidar_pami* lidar = nullptr);
  ~ReturnToStartAction() override = default;

  void start() override;
  void update() override;
  void stop() override;
  bool isFinished() const override;
  const char* name() const override { return "ReturnToStart"; }

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
