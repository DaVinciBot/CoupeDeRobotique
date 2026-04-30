#ifndef ACTIONS_ATOB_H
#define ACTIONS_ATOB_H

#include "action.h"
#include "rolling_basis.h"

class AtoB : public Action {
   public:
    AtoB(RollingBasis* rb, const Point& target);
    ~AtoB() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    RollingBasis* _rb;
    Point _target;
    unsigned long _startMs = 0;
    unsigned long _timeoutMs = 15000;  // Ms
    float _arriveTolMm = 20.0f;
    bool _finished = false;
};

#endif
