#ifndef STRATEGIES_STRATEGY_H
#define STRATEGIES_STRATEGY_H

#include <Arduino.h>
#include "action.h"
#include "navigation.h"
#include "point.h"

class Strategy {
   public:
    Strategy(Navigation* nav, Action** actions, size_t count);
    virtual ~Strategy() = default;

    virtual void start();
    virtual void update();
    virtual void stop();
    virtual bool isFinished() const;
    virtual const char* name() const = 0;

   protected:
    Navigation* _nav;
    Action** _actions;
    size_t _actionCount;
    size_t _currentIndex;
    bool _finished;
    bool _failed;

   private:
    void _startCurrentAction();
};

#endif