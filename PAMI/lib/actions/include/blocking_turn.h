#ifndef ACTIONS_BLOCKING_TURN_H
#define ACTIONS_BLOCKING_TURN_H

#include "action.h"
#include "rolling_basis.h"

class BlockingTurn : public Action {
   public:
    BlockingTurn(RollingBasis* rb, float angleRad);

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    RollingBasis* _rb;
    float _angleRad;
    bool _started = false;
    bool _finished = false;
};

#endif
