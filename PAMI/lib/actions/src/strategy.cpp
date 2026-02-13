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
    Serial.println("Carre started");
    _finished = false;
    _startMs = millis();

    // Lire la pose actuelle (A)
    Point cur = _rb->getPose();
    Serial.printf("Carre::start cur=(%.1f,%.1f,%.3f)\n", cur.x, cur.y, cur.theta);

    // Calculer la cible B en fonction de la distance relative
    Point _target = cur;
    _target.x += _distance * cos(cur.theta);
    _target.y += _distance * sin(cur.theta);
    _target.theta += M_PI / 2; // tourner de 90 degrés pour le prochain côté
    Serial.printf("Carre side %d target=(%.1f,%.1f,%.3f)\n", _sideIndex, _target.x, _target.y, _target.theta);

    // Envoyer la commande vers la cible B
    _rb->setCommand(_target);
    Serial.println("Carre: command sent to rolling basis");
}

void Strategy::update(){
    if (_currentActionIndex >= _actionCount) {
        return;
    }
    Action* currentAction = _actions[_currentActionIndex];
    

void Carre::stop() {
    Serial.println("Carre stopped");
    _rb->stop();
    _finished = true;
}

bool Carre::isFinished() const {
    return _finished;
}

const char* Carre::name() const {
    return "Carre";
}
