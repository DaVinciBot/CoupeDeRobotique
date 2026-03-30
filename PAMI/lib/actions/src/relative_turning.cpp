#include "relative_turning.h"

RelativeTurning::RelativeTurning(RollingBasis* rb, const double angle)
    : _rb(rb), _angle(angle) {
    // valeurs par défaut déjà initialisées inline dans le header,
    // mais on peut ré-initialiser ici si besoin
    _startMs = 0;
    _finished = false;
    Serial.printf("RelativeTurning: angle set to %.1f rad\n", _angle);
    // timeout et tolérance définis dans le header (_timeoutMs, _arriveTolMm)
}

void RelativeTurning::start() {
    Serial.println("RelativeTurning started");
    _finished = false;
    _startMs = millis();

    // Lire la pose actuelle (A)
    Point cur = _rb->getPose();
    Serial.printf("RelativeTurning::start cur=(%.1f,%.1f,%.3f)\n", cur.x, cur.y,
                  cur.theta);
    // Calculer la cible B en fonction de l'angle relatif
    _target = cur;
    _target.theta += _angle;
    Serial.printf("RelativeTurning::start target=(%.1f,%.1f,%.3f)\n", _target.x,
                  _target.y, _target.theta);

    // Envoyer la commande vers la cible B
    _rb->setCommand(_target);
    Serial.println("RelativeForward: command sent to rolling basis");
}

void RelativeTurning::update() {
    // tick the rolling basis controller
    _rb->update();

    if (_finished) {
        return;
    }

    // timeout check
    if (millis() - _startMs > _timeoutMs) {
        Serial.println("RelativeTurning: timeout, stopping");
        _rb->stop();
        _finished = true;
        return;
    }
    // a modifier : pas finis, le dist a changer, et regarder les éventuelles
    // autres fonctions read current pose (may be static if odometry is
    // disabled)
    Point cur = _rb->getPose();
    float angleDiff = _target.theta - cur.theta;

    while (angleDiff > PI) angleDiff -= 2 * PI;
    while (angleDiff < -PI) angleDiff += 2 * PI;
    Serial.printf("RelativeTurning::update angle=%.1f rad\n", angleDiff);
    // arrival condition: within tolerance OR base reports idle
    if (abs(angleDiff) <= _arriveTolRad || !_rb->isMoving()) {
        Serial.println("RelativeTurning: arrived or motors idle -> finishing");
        _rb->stop();
        _finished = true;
    }
}

void RelativeTurning::stop() {
    Serial.println("RelativeTurning stopped");
    _rb->stop();
    _finished = true;
}

bool RelativeTurning::isFinished() const {
    return _finished;
}

const char* RelativeTurning::name() const {
    return "RelativeTurning";
}
