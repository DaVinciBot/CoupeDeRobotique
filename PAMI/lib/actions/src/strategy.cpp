#include "strategy.h"

Strategy::Strategy(RollingBasis* rb) : _rb(rb), _currentActionIndex(0) {
    // valeurs par défaut déjà initialisées inline dans le header,
    // mais on peut ré-initialiser ici si besoin
    for (int i = 0; i < 10; i++) {
        _actions[i] = nullptr;
    }
    initActions();
}

void Strategy::initActions() {
    _actions[0] = new Carre(_rb, 200, 0);
    _actions[1] = new Triangle(_rb, 200, 0);
    _actionCount = 2;
}

void Strategy::start() {
    _currentActionIndex = 0;
    if (_actionCount > 0) {
        Serial.println("Strategy started");
        _actions[_currentActionIndex]->start();
    }
}

void Strategy::update() {
    if (_currentActionIndex >= _actionCount) {
        return;
    }
    Action* currentAction = _actions[_currentActionIndex];
    currentAction->update();
    if (currentAction->isFinished()) {
        Serial.printf("Strategy: action %d finished\n", _currentActionIndex);
        currentAction->stop();
        _currentActionIndex++;
        voyons if (_currentActionIndex < _actionCount) {
            Serial.printf("Strategy: starting action %d\n",
                          _currentActionIndex);
            _actions[_currentActionIndex]->start();
        }
    }
}
void Strategy::stop() {
    if (_currentActionIndex < _actionCount) {
        Serial.println("Strategy stopped");
        _actions[_currentActionIndex]->stop();
    }
}

bool Strategy::isFinished() const {
    return _currentActionIndex >= _actionCount;
}

const char* Strategy::name() const {
    return "Strategy";
}
