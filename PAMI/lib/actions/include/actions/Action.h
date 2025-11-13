// Action.h - interface for high-level robot actions
#pragma once

#include <Arduino.h>

namespace actions {

class Action {
public:
  virtual ~Action() = default;
  // Called once when the action is started
  virtual void start() = 0;
  // Called frequently from the main loop; must be non-blocking
  virtual void update() = 0;
  // Request the action to stop / cleanup
  virtual void stop() = 0;
  // Return true when action finished (success or fail)
  virtual bool isFinished() const = 0;
  // Human readable name for logs
  virtual const char* name() const = 0;
};

} // namespace actions
