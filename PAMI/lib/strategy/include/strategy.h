#ifndef STRATEGIES_STRATEGY_H
#define STRATEGIES_STRATEGY_H

#include <Arduino.h>
#include <vector>

#include "action.h"
#include "rolling_basis.h"

class Strategy {
   public:
    explicit Strategy(RollingBasis* rb);
    Strategy(RollingBasis* rb, const std::vector<Action*>& actions);
    ~Strategy();

    void addAction(Action* action);
    void clearActions();

    void start();
    void update();
    void stop();
    bool isFinished() const;
    const char* name() const;

   private:
    RollingBasis* _rb;
    std::vector<Action*> _actions;
    size_t _currentIndex = 0;
    bool _started = false;
    bool _finished = false;
    bool _stopped = false;

    void startCurrentAction();
};

#endif
