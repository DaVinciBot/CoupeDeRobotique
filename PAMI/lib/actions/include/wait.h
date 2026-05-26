#ifndef ACTIONS_WAIT_H
#define ACTIONS_WAIT_H

#include "action.h"

class Wait : public Action {
   public:
    Wait(unsigned long durationMs);

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    unsigned long _durationMs;
    unsigned long _startMs = 0;
    bool _finished = false;
};

#endif
