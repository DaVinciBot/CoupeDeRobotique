#include "navigation.h"

Navigation::Navigation(RollingBasis* basis, uint32_t timeoutMs)
    : _basis(basis),
      _sendIntervalMs(timeoutMs / DEFAULT_SEGMENTS),
      _timeoutMs(timeoutMs),
      _lastSendMs(0),
      _startMs(0),
      _lastTarget{0, 0, 0} {}

void Navigation::setCommand(const Point& targetPos) {
    _lastTarget = targetPos;
    _startMs = millis();
    _lastSendMs = 0;

    _waypoints.clear();
    Point start = _basis->getPose();
    float angle = start.theta + Point::angle(start, targetPos);
    for (size_t i = 1; i <= DEFAULT_SEGMENTS; ++i) {
        float t = float(i) / DEFAULT_SEGMENTS;
        Point wp;
        wp.x = start.x + t * (targetPos.x - start.x);
        wp.y = start.y + t * (targetPos.y - start.y);
        wp.theta = angle;
        _waypoints.push_back(wp);
    }
    _wpIndex = 0;
    _basis->setCommand(_waypoints[_wpIndex]);
}

void Navigation::setTrajectory(const std::vector<Point>& trajectory) {
    if (trajectory.empty()) {
        Serial.println("[Navigation] Erreur: trajectoire vide!");
        return;
    }

    _waypoints.clear();
    Point start = _basis->getPose();  // Position actuelle du robot (maintenant correctement mise à jour)

    // Pour chaque point de la trajectoire, créer les waypoints intermédiaires
    for (const Point& targetPos : trajectory) {
        // Utiliser l'angle fourni dans le point
        float angle = targetPos.theta;

        // Créer les waypoints intermédiaires comme dans setCommand()
        for (size_t i = 1; i <= DEFAULT_SEGMENTS; ++i) {
            float t = float(i) / DEFAULT_SEGMENTS;
            Point wp;
            wp.x = start.x + t * (targetPos.x - start.x);
            wp.y = start.y + t * (targetPos.y - start.y);
            wp.theta = angle;
            _waypoints.push_back(wp);
        }

        // Mettre à jour start avec la position RÉELLE du robot (via getPose())
        // Cela revient à supposer que le robot atteint précisément chaque waypoint
        start = _basis->getPose();
    }

    _wpIndex = 0;
    _startMs = millis();
    _lastSendMs = 0;

    if (!_waypoints.empty()) {
        _basis->setCommand(_waypoints[0]);
        Serial.printf("[Navigation] Trajectoire chargée avec %d segments\n", _waypoints.size());
    }
}

void Navigation::update() {
    
    uint32_t now = millis();

    // force stop after timeout
    if (_startMs && now - _startMs >= _timeoutMs) {
        stop();
        return;
    }

    // resend every interval
    if (_lastSendMs == 0 || now - _lastSendMs >= _sendIntervalMs ||
        _basis->isMoving() == false) {
        if (_wpIndex >= _waypoints.size()) {
            Serial.println("[Navigation] No more waypoints to send.");
            return;  // no more waypoints to send
        } else if (_wpIndex + 1 < _waypoints.size()) {
            _basis->setCommand(_waypoints[++_wpIndex]);
        }
        _lastSendMs = now;
        Serial.printf("[Navigation] Sending command to basis: %d, %d, %d\n",
                      _waypoints[_wpIndex].x, _waypoints[_wpIndex].y,
                      _waypoints[_wpIndex].theta);
    }
    _basis->update();
}

bool Navigation::isMoving() const {
    return _basis->isMoving();
}

void Navigation::stop() {
    _basis->stop();
    _startMs = 0;
}

Point Navigation::getPose() const {
    return _basis->getPose();
}

float Navigation::getMeasuredLinearSpeed() const {
    return _basis->getLinearSpeedMmPerS();
}

float Navigation::getMeasuredAngularSpeed() const {
    return _basis->getAngularSpeedRadPerS();
}
