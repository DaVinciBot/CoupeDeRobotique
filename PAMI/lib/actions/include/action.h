#ifndef ACTIONS_ACTION_H
#define ACTIONS_ACTION_H

#include <Arduino.h>

class Action {
   public:
    virtual ~Action() = default;
    virtual void start() = 0;
    virtual void update() = 0;
    virtual void stop() = 0;
    virtual bool isFinished() const = 0;
    virtual const char* name() const = 0;
};

#endif
