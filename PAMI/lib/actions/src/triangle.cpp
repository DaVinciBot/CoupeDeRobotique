#include "triangle.h"

Triangle::Triangle(RollingBasis* rb, const double length, const double angle)
    : _rb(rb), _distance(length) {
    // valeurs par défaut déjà initialisées inline dans le header,
    // mais on peut ré-initialiser ici si besoin
    _startMs = 0;
    _finished = false;
    _sideIndex = 0;
    Serial.printf("Carre: length set to %.1f mm\n", _distance);
    // timeout et tolérance définis dans le header (_timeoutMs, _arriveTolMm)
}

void Triangle::start() {
    Serial.println("Triangle started");
    _finished = false;
    _startMs = millis();

    // Lire la pose actuelle (A)
    Point cur = _rb->getPose();
    Serial.printf("Triangle::start cur=(%.1f,%.1f,%.3f)\n", cur.x, cur.y,
                  cur.theta);

    // Calculer la cible B en fonction de la distance relative
    _target = cur;
    _target.x += _distance * cos(cur.theta);
    _target.y += _distance * sin(cur.theta);
    _target.theta +=
        2 * M_PI / 3;  // tourner de 120 degrés pour le prochain côté
    Serial.printf("Triangle side %d target=(%.1f,%.1f,%.3f)\n", _sideIndex,
                  _target.x, _target.y, _target.theta);

    // Envoyer la commande vers la cible B
    _rb->setCommand(_target);
    Serial.println("Triangle: command sent to rolling basis");
}

void Triangle::update() {
    // tick the rolling basis controller
    _rb->update();

    if (_finished) {
        return;
    }

    // timeout check
    if (millis() - _startMs > _timeoutMs) {
        Serial.println("Triangle: timeout, stopping");
        _rb->stop();
        _finished = true;
        return;
    }

    // read current pose (may be static if odometry is disabled)
    Point cur = _rb->getPose();
    float dist = Point::distance(cur, _target);
    Serial.printf("Triangle::update dist=%.1f mm\n", dist);
    // arrival condition: within tolerance OR base reports idle
    if (dist <= _arriveTolMm || !_rb->isMoving()) {
        Serial.println("Triangle: arrived or motors idle -> finishing");
        _rb->stop();
        _sideIndex++;
        if (_sideIndex >= 3) {
            _finished = true;
            _sideIndex = 0;
            return;
        }
        start();
    }
}

void Triangle::stop() {
    Serial.println("Triangle stopped");
    _rb->stop();
    _finished = true;
}

bool Triangle::isFinished() const {
    return _finished;
}

const char* Triangle::name() const {
    return "Triangle";
}
