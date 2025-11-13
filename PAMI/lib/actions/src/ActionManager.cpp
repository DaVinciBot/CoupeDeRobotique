#include "actions/ActionManager.h"
#include <Arduino.h>

using namespace actions;

ActionManager::~ActionManager() {
  // cleanup queue
  if (_current) {
    _current->stop();
    delete _current;
    _current = nullptr;
  }
  for (auto *a : _queue) delete a;
  _queue.clear();
}

void ActionManager::push(Action* a) {
  if (!a) return;
  _queue.push_back(a);
}

void ActionManager::update() {
  // start next if none running
  if (!_current && !_queue.empty()) {
    _current = _queue.front();
    _queue.erase(_queue.begin());
    Serial.printf("ActionManager: starting %s\n", _current->name());
    _current->start();
  }

  if (_current) {
    _current->update();
    if (_current->isFinished()) {
      Serial.printf("ActionManager: finished %s\n", _current->name());
      _current->stop();
      delete _current;
      _current = nullptr;
    }
  }
}

void ActionManager::abortCurrent() {
  if (_current) {
    Serial.printf("ActionManager: aborting %s\n", _current->name());
    _current->stop();
    delete _current;
    _current = nullptr;
  }
}

Action* ActionManager::current() const { return _current; }
