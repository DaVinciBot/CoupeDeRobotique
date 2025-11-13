// ActionManager.h - simple FIFO action manager
#pragma once

#include "Action.h"
#include <vector>

namespace actions {

class ActionManager {
public:
  ActionManager() = default;
  ~ActionManager();

  // Manager takes ownership of the pointer (will delete when done)
  void push(Action* a);
  // Call from main loop
  void update();
  // Abort current action immediately
  void abortCurrent();
  // Returns current action or nullptr
  Action* current() const;

private:
  std::vector<Action*> _queue;
  Action* _current = nullptr;
};

} // namespace actions
