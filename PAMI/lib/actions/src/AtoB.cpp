#include "AtoB.h"

AtoB::AtoB(RollingBasis* rb, const Point& target) : _rb(rb), _target(target) {
    // valeurs par défaut déjà initialisées inline dans le header,
    // mais on peut ré-initialiser ici si besoin
    _startMs = 0;
    _finished = false;
    Serial.printf("AtoB: target set to x=%.1f y=%.1f theta=%.3f\n", _target.x,
                  _target.y, _target.theta);
    // timeout et tolérance définis dans le header (_timeoutMs, _arriveTolMm)
}

void AtoB::start() {
    Serial.println("[AtoB] START");
    _finished = false;
    _startMs = millis();

    // Lire la pose actuelle (A)
    Point cur = _rb->getPose();
    Serial.printf("[AtoB] cur=(%.1f,%.1f,%.3f)\n", cur.x, cur.y, cur.theta);

    // Envoyer la commande vers la cible B (doit avoir été définie via setTarget)
    _rb->setCommand(_target);
    Serial.printf("[AtoB] target=(%.1f,%.1f,%.3f)\n", _target.x, _target.y, _target.theta);
    Serial.printf("[AtoB] RB isMoving after setCommand: %d\n", _rb->isMoving());
    Serial.println("[AtoB] command sent to rolling basis");
}

void AtoB::update() {
    // tick the rolling basis controller
    _rb->update();

    if (_finished) {
        return;
    }

    // timeout check
    if (millis() - _startMs > _timeoutMs) {
        Serial.println("[AtoB] TIMEOUT!");
        _finished = true;
        return;
    }

    // read current pose (may be static if odometry is disabled)
    Point cur = _rb->getPose();
    float dist = Point::distance(cur, _target);
    
    // Only print every 1 second to avoid spam
    static unsigned long lastPrint = 0;
    if (millis() - lastPrint > 1000) {
        Serial.printf("[AtoB] dist=%.1f mm, isMoving=%d\n", dist, _rb->isMoving());
        lastPrint = millis();
    }

    // arrival condition: within tolerance OR base reports idle
    if (dist <= _arriveTolMm || !_rb->isMoving()) {
        Serial.printf("[AtoB] ✓ ARRIVED or IDLE! (dist=%.1f, moving=%d)\n", dist, _rb->isMoving());
        _finished = true;
    }
}

void AtoB::stop() {
    Serial.println("AtoB stopped");
    _rb->stop();
    _finished = true;
}

bool AtoB::isFinished() const {
    return _finished;
}

const char* AtoB::name() const {
    return "AtoB";
}
