#include "relative_forward.h"

RelativeForward::RelativeForward(RollingBasis* rb, const double distance) : _rb(rb), _distance(distance) {
    // valeurs par défaut déjà initialisées inline dans le header,
    // mais on peut ré-initialiser ici si besoin
    _startMs = 0;
    _finished = false;
    Serial.printf("RelativeForward: distance set to %.1f mm\n", _distance);
    // timeout et tolérance définis dans le header (_timeoutMs, _arriveTolMm)
}

void RelativeForward::start() {
    Serial.println("RelativeForward started");
    _finished = false;
    _startMs = millis();

    // Lire la pose actuelle (A)
    Point cur = _rb->getPose();
    Serial.printf("RelativeForward::start cur=(%.1f,%.1f,%.3f)\n", cur.x, cur.y, cur.theta);

    // Calculer la cible B en fonction de la distance relative
    Point _target = cur;
    _target.x += _distance * cos(cur.theta);
    _target.y += _distance * sin(cur.theta);
    Serial.printf("RelativeForward::start target=(%.1f,%.1f,%.3f)\n", _target.x, _target.y, _target.theta);

    // Envoyer la commande vers la cible B
    _rb->setCommand(_target);
    Serial.println("RelativeForward: command sent to rolling basis");
}

void RelativeForward::update() {
    // tick the rolling basis controller
    _rb->update();

    if (_finished) {
        return;
    }

    // timeout check
    if (millis() - _startMs > _timeoutMs) {
        Serial.println("RelativeForward: timeout, stopping");
        _rb->stop();
        _finished = true;
        return;
    }

    // read current pose (may be static if odometry is disabled)
    Point cur = _rb->getPose();
    float dist = Point::distance(cur, _target);
    Serial.printf("RelativeForward::update dist=%.1f mm\n", dist);
    // arrival condition: within tolerance OR base reports idle
    if (dist <= _arriveTolMm || !_rb->isMoving()) {
        Serial.println("RelativeForward: arrived or motors idle -> finishing");
        _rb->stop();
        _finished = true;
    }
}

void RelativeForward::stop() {
    Serial.println("RelativeForward stopped");
    _rb->stop();
    _finished = true;
}

bool RelativeForward::isFinished() const {
    return _finished;
}

const char* RelativeForward::name() const {
    return "RelativeForward";
}
