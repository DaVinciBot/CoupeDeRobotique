#include "strategy.h"

Strategy::Strategy(RollingBasis* rb) : _rb(rb) {}

Strategy::Strategy(RollingBasis* rb, const std::vector<Action*>& actions)
    : _rb(rb), _actions(actions) {}

Strategy::~Strategy() {
    clearActions();
}

void Strategy::addAction(Action* action) {
    if (action == nullptr) {
        Serial.println("[Strategy] Ignored null action");
        return;
    }

    _actions.push_back(action);
    _finished = false;

    Serial.printf("[Strategy] Action added: %s (total: %u)\n", action->name(),
                  static_cast<unsigned>(_actions.size()));
}

void Strategy::clearActions() {
    if (_started && !isFinished() && _currentIndex < _actions.size()) {
        _actions[_currentIndex]->stop();
    }

    for (Action* action : _actions) {
        delete action;
    }

    _actions.clear();
    _currentIndex = 0;
    _started = false;
    _finished = false;
    _stopped = false;
}

void Strategy::startCurrentAction() {
    if (_currentIndex >= _actions.size()) {
        _finished = true;
        return;
    }

    Action* currentAction = _actions[_currentIndex];
    Serial.printf("[Strategy] Starting action %u/%u: %s\n",
                  static_cast<unsigned>(_currentIndex + 1),
                  static_cast<unsigned>(_actions.size()),
                  currentAction->name());
    currentAction->start();
}

void Strategy::start() {
    _currentIndex = 0;
    _started = true;
    _finished = false;
    _stopped = false;

    if (_actions.empty()) {
        Serial.println("[Strategy] No action to run");
        _finished = true;
        return;
    }

    Serial.println("[Strategy] Started");
    startCurrentAction();
}

void Strategy::update() {
    if (!_started || _finished || _stopped) {
        return;
    }

    if (_currentIndex >= _actions.size()) {
        _finished = true;
        return;
    }

    Action* currentAction = _actions[_currentIndex];
    currentAction->update();

    if (!currentAction->isFinished()) {
        return;
    }

    Serial.printf("[Strategy] Finished action %u/%u: %s\n",
                  static_cast<unsigned>(_currentIndex + 1),
                  static_cast<unsigned>(_actions.size()),
                  currentAction->name());

    _currentIndex++;

    if (_currentIndex >= _actions.size()) {
        _finished = true;
        Serial.println("[Strategy] All actions finished");
        return;
    }

    startCurrentAction();
}

void Strategy::stop() {
    if (!_finished && _currentIndex < _actions.size()) {
        _actions[_currentIndex]->stop();
    }

    _stopped = true;
    _finished = true;
    Serial.println("[Strategy] Stopped");
}

bool Strategy::isFinished() const {
    return _finished || _stopped;
}

const char* Strategy::name() const {
    return "Strategy";
}
