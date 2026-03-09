#ifndef ACTIONS_TRIANGLE_H
#define ACTIONS_TRIANGLE_H

#include "action.h"
#include "rolling_basis.h"

class Triangle : public Action {
   public:
    Triangle(RollingBasis* rb, const double length, const double angle);
    ~Triangle() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    Point _target;
    int _sideIndex = 0;  // 0 → 3
    RollingBasis* _rb;
    const double _distance;
    unsigned long _startMs = 0;
    unsigned long _timeoutMs = 15000;  // Ms
    float _arriveTolRad = 5.0f;
    float _arriveTolMm = 5.0f;
    bool _finished = false;
};

#endif
