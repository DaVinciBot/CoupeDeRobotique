#include "relative_backward.h"

RelativeBackward::RelativeBackward(Navigation* nav, const double distance)
    : _navigation(nav), _distance(distance) {
    // valeurs par défaut déjà initialisées inline dans le header,
    // mais on peut ré-initialiser ici si besoin
    _startMs = 0;
    _finished = false;
    Serial.printf("RelativeBackward: distance set to %.1f mm\n", _distance);
    // timeout et tolérance définis dans le header (_timeoutMs, _arriveTolMm)
}

void RelativeBackward::start() {
    Serial.println("RelativeBackward started");
    _finished = false;
    _startMs = millis();

    // Lire la pose actuelle (A)
    Point cur = _navigation->getPose();
    Serial.printf("RelativeBackward::start cur=(%.1f,%.1f,%.3f)\n", cur.x, cur.y,
                  cur.theta);

    // Calculer la cible B en fonction de la distance relative
    _target = cur;
    _target.x -= _distance * cos(cur.theta);
    _target.y -= _distance * sin(cur.theta);
    Serial.printf("RelativeBackward::start target=(%.1f,%.1f,%.3f)\n", _target.x,
                  _target.y, _target.theta);

    // Envoyer la commande vers la cible B
    _navigation->setCommand(_target);
    Serial.println("RelativeBackward: command sent to rolling basis");
}

void RelativeBackward::update() {
    // tick the rolling basis controller
    _navigation->update();

    if (_finished) {
        return;
    }

    // timeout check
    if (millis() - _startMs > _timeoutMs) {
        Serial.println("RelativeBackward: timeout, stopping");
        _navigation->stop();
        _finished = true;
        return;
    }

    // read current pose (may be static if odometry is disabled)
    Point cur = _navigation->getPose();
    float dist = Point::distance(cur, _target);
    Serial.printf("RelativeBackward::update dist=%.1f mm\n", dist);
    // arrival condition: within tolerance OR base reports idle
    if (dist <= _arriveTolMm || !_navigation->isMoving()) {
        Serial.println("RelativeBackward: arrived or motors idle -> finishing");
        _navigation->stop();
        _finished = true;
    }
}

void RelativeBackward::stop() {
    Serial.println("RelativeBackward stopped");
    _navigation->stop();
    _finished = true;
}

bool RelativeBackward::isFinished() const {
    return _finished;
}

const char* RelativeBackward::name() const {
    return "RelativeBackward";
}
