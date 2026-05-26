#ifndef ACTIONS_ACTIONNEUR_H
#define ACTIONS_ACTIONNEUR_H

#include "action.h"

class Actionneur : public Action {
   public:
    Actionneur(uint8_t pin);
    ~Actionneur() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

    void setAngle(uint16_t angle);
    uint16_t getAngle() const;

   private:
    uint8_t _pin;
    uint16_t _currentAngle = 0;
    uint16_t _targetAngle = 0;
    unsigned long _startMs = 0;
    unsigned long _timeoutMs = 5000;  // Ms
    bool _finished = false;
};

#endif
