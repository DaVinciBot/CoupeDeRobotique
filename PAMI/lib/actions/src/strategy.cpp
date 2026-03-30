#include "strategy.h"
#include <vector>
Strategy::Strategy(RollingBasis* rb) : _rb(rb), _currentActionIndex(0) {
    // valeurs par défaut déjà initialisées inline dans le header,
    // mais on peut ré-initialiser ici si besoin
    initActions();
}

void Strategy::initActions() {
    _actions.push_back(new Carre(_rb, 200, 0));
    _actions.push_back(new Triangle(_rb, 200, 0));
}

void Strategy::start() {
    _currentActionIndex = 0;
    if (_actions.size() > 0) {
        Serial.println("Strategy started");
        _actions[_currentActionIndex]->start();
    }
}

void Strategy::update() {
    if (_currentActionIndex >= _actions.size()) {
        return;
    }
    Action* currentAction = _actions[_currentActionIndex];
    currentAction->update();
    if (currentAction->isFinished()) {
        Serial.printf("Strategy: action %d finished\n", _currentActionIndex);
        currentAction->stop();
        _currentActionIndex++;
        if (_currentActionIndex < _actions.size()) {
            Serial.printf("Strategy: starting action %d\n",
                          _currentActionIndex);
            _actions[_currentActionIndex]->start();
        }
    }
}
void Strategy::stop() {
    if (_currentActionIndex < _actions.size()) {
        Serial.println("Strategy stopped");
        _actions[_currentActionIndex]->stop();
    }
}

bool Strategy::isFinished() const {
    return _currentActionIndex >= _actions.size();
}

const char* Strategy::name() const {
    return "Strategy";
}
