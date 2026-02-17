#include "strategy.h"

Strategy::Strategy(RollingBasis* rb) : _rb(rb), _currentActionIndex(0) { // Initialize the sequence of actions for the strategy // For example, we can define a simple sequence of actions here _actions[0] = new AtoB(_rb, {200, 0, 0}); // Move forward 200mm _actions[1] = new RelativeTurning(_rb, M_PI / 2); // Turn 90 degrees _actions[2] = new RelativeForward(_rb, 100); // Move forward 100mm _actions[3] = new RelativeTurning(_rb, M_PI / 2); // Turn 90 degrees _actions[4] = new RelativeForward(_rb, 100); // Move forward 100mm _actions[5] = new RelativeTurning(_rb, M_PI / 2); // Turn 90 degrees _actions[6] = new RelativeForward(_rb, 100); // Move forward 100mm _actions[7] = new RelativeTurning(_rb, M_PI / 2); // Turn 90 degrees _actions[8] = new RelativeForward(_rb, 100); // Move forward 100mm _actionCount = 9; } void Strategy::start() { if (_actionCount > 0) { Serial.println("Strategy started"); _currentActionIndex = 0; _actions[_currentActionIndex]->start(); } } void Strategy::update() { if (_currentActionIndex < _actionCount) { Action* currentAction = _actions[_currentActionIndex]; currentAction->update(); if (currentAction->isFinished()) { Serial.printf("Strategy: action %d finished\n", _currentActionIndex); currentAction->stop(); _currentActionIndex++; if (_currentActionIndex < _actionCount) { Serial.printf("Strategy: starting action %d\n", _currentActionIndex); _actions[_currentActionIndex]->start(); } } } } void Strategy::stop() { if (_currentActionIndex < _actionCount) { Serial.println("Strategy stopped"); _actions[_currentActionIndex]->stop(); } } bool Strategy::isFinished() const { return _currentAction
    // valeurs par défaut déjà initialisées inline dans le header,
    // mais on peut ré-initialiser ici si besoin
    for (int i = 0; i <10; i++) {
        _actions[i] = nullptr;}
    initActions();
}
void Strategy::initActions() {
    _actions[0] = new Carre(_rb, 200, 0); 
    _actions[1] = new Triangle(_rb, 200, 0); 
    _actionCount = 2; 
}
    
    
    // Initialize the sequence of actions for the strategy // For example, we can define a simple sequence of actions here _actions[0] = new AtoB(_rb, {200, 0, 0}); // Move forward 200mm _actions[1] = new RelativeTurning(_rb, M_PI / 2); // Turn 90 degrees _actions[2] = new RelativeForward(_rb, 100); // Move forward 100mm _actions[3] = new RelativeTurning(_rb, M_PI / 2); // Turn 90 degrees _actions[4] = new RelativeForward(_rb, 100); // Move forward 100mm _actions[5] = new RelativeTurning(_rb, M_PI / 2); // Turn 90 degrees _actions[6] = new RelativeForward(_rb, 100); // Move forward 100mm _actions[7] = new RelativeTurning(_rb, M_PI / 2); // Turn 90 degrees _actions[8] = new RelativeForward(_rb, 100); // Move forward 100mm _actionCount = 9; }
void Strategy::start() {
    _currentActionIndex = 0;
    if (_actionCount > 0) {
        Serial.println("Strategy started");
        _actions[_currentActionIndex]->start();
    }
}

void Strategy::update(){
    if (_currentActionIndex >= _actionCount) {
        return;
    }
    Action* currentAction = _actions[_currentActionIndex];
    currentAction->update();
    if (currentAction->isFinished()) {
        Serial.printf("Strategy: action %d finished\n", _currentActionIndex);
        currentAction->stop();
        _currentActionIndex++;
        if (_currentActionIndex < _actionCount) {
            Serial.printf("Strategy: starting action %d\n", _currentActionIndex);
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
