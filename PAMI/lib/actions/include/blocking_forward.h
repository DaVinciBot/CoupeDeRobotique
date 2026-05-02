#ifndef ACTIONS_BLOCKING_FORWARD_H
#define ACTIONS_BLOCKING_FORWARD_H

#include "action.h"
#include "rolling_basis.h"

class BlockingForward : public Action {
   public:
    BlockingForward(RollingBasis* rb, float distanceMm);

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    RollingBasis* _rb;
    float _distanceMm;
    bool _started = false;
    bool _finished = false;
};

#endif
