#include "carre.h"

Carre::Carre(RollingBasis* rb, const double length, const double angle)
    : _rb(rb), _distance(length) {
    // valeurs par défaut déjà initialisées inline dans le header,
    // mais on peut ré-initialiser ici si besoin
    _startMs = 0;
    _finished = false;
    _sideIndex = 0;
    Serial.printf("Carre: length set to %.1f mm\n", _distance);
    // timeout et tolérance définis dans le header (_timeoutMs, _arriveTolMm)
}

void Carre::start() {
    Serial.println("Carre started");
    _finished = false;
    _startMs = millis();

    // Lire la pose actuelle (A)
    Point cur = _rb->getPose();
    Serial.printf("Carre::start cur=(%.1f,%.1f,%.3f)\n", cur.x, cur.y,
                  cur.theta);

    // Calculer la cible B en fonction de la distance relative
    _target = cur;
    _target.x += _distance * cos(cur.theta);
    _target.y += _distance * sin(cur.theta);
    _target.theta += M_PI / 2;  // tourner de 90 degrés pour le prochain côté
    Serial.printf("Carre side %d target=(%.1f,%.1f,%.3f)\n", _sideIndex,
                  _target.x, _target.y, _target.theta);

    // Envoyer la commande vers la cible B
    _rb->setCommand(_target);
    Serial.println("Carre: command sent to rolling basis");
}

void Carre::update() {
    // tick the rolling basis controller
    _rb->update();

    if (_finished) {
        return;
    }

    // timeout check
    if (millis() - _startMs > _timeoutMs) {
        Serial.println("Carre: timeout, stopping");
        _rb->stop();
        _finished = true;
        return;
    }

    // read current pose (may be static if odometry is disabled)
    Point cur = _rb->getPose();
    float dist = Point::distance(cur, _target);
    Serial.printf("Carre::update dist=%.1f mm\n", dist);
    // arrival condition: within tolerance OR base reports idle
    if (dist <= _arriveTolMm || !_rb->isMoving()) {
        Serial.println("Carre: arrived or motors idle -> finishing");
        _rb->stop();
        _sideIndex++;
        if (_sideIndex >= 4) {
            _finished = true;
            _sideIndex = 0;
            return;
        }
        start();
    }
}

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
