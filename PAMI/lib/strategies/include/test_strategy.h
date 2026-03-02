#ifndef STRATEGIES_TEST_STRATEGY_H
#define STRATEGIES_TEST_STRATEGY_H

#include "strategy.h"

class TestStrategy : public Strategy {
   public:
    TestStrategy(Navigation* nav, Action** actions, size_t count)
        : Strategy(nav, actions, count) {}

    const char* name() const override { return "TestStrategy"; }
};

#endif