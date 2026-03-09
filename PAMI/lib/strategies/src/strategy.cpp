#include "strategy.h"

Strategy::Strategy(RollingBasis* rb)
    : _rb(rb), _currentIndex(0), _finished(false), _failed(false) {}

void Strategy::addAction(Action* action) {
    _actions.push_back(action);
    Serial.printf("[Strategy] Action ajoutée : %s (total: %d)\n",
                  action->name(), _actions.size());
}

void Strategy::_startCurrentAction() {
    Serial.printf("[Strategy:%s] Action %d/%d : %s\n", name(),
                  _currentIndex + 1, _actions.size(),
                  _actions[_currentIndex]->name());
    _actions[_currentIndex]->start();
}

void Strategy::start() {
    _currentIndex = 0;
    _finished = false;
    _failed = false;

    if (_actions.empty()) {
        Serial.println("[Strategy] Aucune action dans la liste.");
        _finished = true;
        return;
    }
    _startCurrentAction();
}

void Strategy::update() {
    if (_finished || _failed)
        return;

    Action* current = _actions[_currentIndex];
    current->update();

    if (current->isFinished()) {
        current->stop();
        Serial.printf("[Strategy:%s] Action terminée : %s\n", name(),
                      current->name());
        _currentIndex++;

        if (_currentIndex >= _actions.size()) {
            _finished = true;
            Serial.printf("[Strategy:%s] Toutes les actions terminées.\n",
                          name());
        } else {
            _startCurrentAction();
        }
    }
}

void Strategy::stop() {
    if (!_finished && _currentIndex < _actions.size()) {
        _actions[_currentIndex]->stop();
    }
    _failed = true;
    Serial.printf("[Strategy:%s] Arrêt forcé.\n", name());
}

bool Strategy::isFinished() const {
    return _finished;
}