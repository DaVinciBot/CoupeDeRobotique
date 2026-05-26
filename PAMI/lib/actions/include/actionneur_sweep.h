#ifndef ACTIONS_ACTIONNEUR_SWEEP_H
#define ACTIONS_ACTIONNEUR_SWEEP_H

#include "action.h"

class ActionneurSweep : public Action {
   public:
    ActionneurSweep(uint8_t pin, unsigned long durationMs);

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    uint8_t _pin;
    unsigned long _durationMs;
    bool _started = false;
    bool _finished = false;

    void setServoAngle(uint8_t angle);
};

#endif
