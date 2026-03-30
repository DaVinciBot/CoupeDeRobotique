#ifndef ACTIONS_RELATIVE_FORWARD_H
#define ACTIONS_RELATIVE_FORWARD_H

#include "action.h"
#include "rolling_basis.h"

class RelativeForward : public Action {
   public:
    RelativeForward(RollingBasis* rb, const double distance);
    ~RelativeForward() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    Point _target;
    RollingBasis* _rb;
    const double _distance;
    unsigned long _startMs = 0;
    unsigned long _timeoutMs = 15000;  // Ms
    float _arriveTolMm = 5.0f;
    bool _finished = false;
};

#endif
