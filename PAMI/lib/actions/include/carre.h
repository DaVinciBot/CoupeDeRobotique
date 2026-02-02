#ifndef ACTIONS_CARRE_H
#define ACTIONS_CARRE_H

#include "action.h"
#include "rolling_basis.h"

class Carre : public Action {
   public:
    Carre(RollingBasis* rb, const double length, const double angle);
    ~Carre() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    const Point _target;
    RollingBasis* _rb;
    const double _distance;
    const double _angle;
    unsigned long _startMs = 0;
    unsigned long _timeoutMs = 15000; // Ms
    float _arriveTolRad = 5.0f;
    float _arriveTolMm = 5.0f;
    bool _finished = false;

};

#endif