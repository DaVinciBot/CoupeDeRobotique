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

// Nouvelle méthode pour passer une trajectoire de points
void Strategy::setPointTrajectory(const std::vector<Point>& points) {
    // Vider les actions existantes
    for (auto action : _actions) {
        delete action;
    }
    _actions.clear();
    _currentActionIndex = 0;
    
    // Créer une action AtoB pour chaque point (avec calibration 0.4)
    for (const Point& p : points) {
        Point calibrated = {p.x * 0.4f, p.y * 0.4f, p.theta};
        _actions.push_back(new AtoB(_rb, calibrated));
        Serial.printf("Strategy: Adding AtoB to point (%.1f, %.1f) - calibrated from (%.1f, %.1f)\n", 
                      calibrated.x, calibrated.y, p.x, p.y);
    }
    Serial.printf("Strategy: Trajectory set with %d points\n", _actions.size());
}

// === NOUVELLES FONCTIONS ===

// Initialise la stratégie avec une liste de points
void Strategy::creer_strategie(const std::vector<Point>& points) {
    Serial.printf("Strategy: Creating with %d points (will be calibrated by 0.4)\n", points.size());
    setPointTrajectory(points);
}

// Ajoute un point à la stratégie (crée un AtoB pour ce point)
void Strategy::ajoute_strategie(const Point& point) {
    Point calibrated = {point.x * 0.4f, point.y * 0.4f, point.theta};
    _actions.push_back(new AtoB(_rb, calibrated));
    Serial.printf("Strategy: Added point (%.1f, %.1f) - calibrated from (%.1f, %.1f). Total actions: %d\n", 
                  calibrated.x, calibrated.y, point.x, point.y, _actions.size());
}

// Update strategy + rolling basis movement
void Strategy::strategie_update() {
    // Update des moteurs d'abord
    _rb->getLeftMotor()->update();
    _rb->getRightMotor()->update();
    
    // Ensuite update la stratégie
    this->update();
}

void Strategy::start() {
    _currentActionIndex = 0;
    _waitingBetweenActions = false;
    if (_actions.size() > 0) {
        Serial.println("Strategy started");
        _actions[_currentActionIndex]->start();
    }
}

void Strategy::update() {
    if (_currentActionIndex >= _actions.size()) {
        //Serial.println("[Strategy] All actions finished!");
        return;
    }
    
    // Gère le délai entre deux actions
    if (_waitingBetweenActions) {
        if (millis() - _transitionDelay > 300) {  // 300ms de délai
            _waitingBetweenActions = false;
            Serial.printf("[Strategy] Transition complete -> Starting action %d\n", _currentActionIndex);
            Serial.printf("[Strategy] RB isMoving before start: %d\n", _rb->isMoving());
            _actions[_currentActionIndex]->start();
        }
        return;
    }
    
    Action* currentAction = _actions[_currentActionIndex];
    currentAction->update();
    
    if (currentAction->isFinished()) {
        Serial.printf("[Strategy] ✓ Action %d FINISHED!\n", _currentActionIndex);
        Serial.printf("[Strategy] RB isMoving before stop: %d\n", _rb->isMoving());
        currentAction->stop();
        Serial.printf("[Strategy] RB isMoving after stop: %d\n", _rb->isMoving());
        _currentActionIndex++;
        
        if (_currentActionIndex < _actions.size()) {
            _transitionDelay = millis();
            _waitingBetweenActions = true;
            Serial.printf("[Strategy] ⏸ Waiting before action %d...\n", _currentActionIndex);
        } else {
            Serial.println("[Strategy] ✓✓ ALL ACTIONS FINISHED!");
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
