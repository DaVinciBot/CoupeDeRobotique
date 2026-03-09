#include "strategy.h"

Strategy::Strategy(Navigation* nav, Action** actions, size_t count)
    : _nav(nav),
      _actions(actions),
      _actionCount(count),
      _currentIndex(0),
      _finished(false),
      _failed(false) {}

void Strategy::_startCurrentAction() {
    Serial.printf("[Strategy:%s] Starting action %d/%d : %s\n", name(),
                  _currentIndex + 1, _actionCount,
                  _actions[_currentIndex]->name());
    _actions[_currentIndex]->start();
}

void Strategy::start() {
    _currentIndex = 0;
    _finished = false;
    _failed = false;

    if (_actionCount == 0) {
        _finished = true;
        return;
    }
    _startCurrentAction();
}

void Strategy::update() {
    if (_finished || _failed)
        return;

    Action* current = _actions[_currentIndex];

    // Injecter la nav dans l'action + faire avancer le mouvement
    _nav->update();
    current->update();

    if (current->isFinished()) {
        current->stop();
        Serial.printf("[Strategy:%s] Action done : %s\n", name(),
                      current->name());

        _currentIndex++;

        if (_currentIndex >= _actionCount) {
            _finished = true;
            Serial.printf("[Strategy:%s] All actions completed.\n", name());
        } else {
            _startCurrentAction();
        }
    }
}

void Strategy::stop() {
    if (!_finished && _currentIndex < _actionCount) {
        _actions[_currentIndex]->stop();
    }
    _nav->stop();
    _failed = true;
    Serial.printf("[Strategy:%s] Stopped (failure or external stop).\n",
                  name());
}

bool Strategy::isFinished() const {
    return _finished;
}