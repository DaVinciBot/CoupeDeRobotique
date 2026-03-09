#ifndef ACTIONS_RELATIVE_BACKWARD_H
#define ACTIONS_RELATIVE_BACKWARD_H

#include "action.h"
#include "rolling_basis.h"

class RelativeBackward : public Action {
   public:
    RelativeBackward(RollingBasis* rb, const double distance);
    ~RelativeBackward() = default;
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
