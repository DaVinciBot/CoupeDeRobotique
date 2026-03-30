#ifndef STRATEGY_H
#define STRATEGY_H
#include <vector>
#include "AtoB.h"
#include "action.h"
#include "actionneur.h"
#include "carre.h"
#include "relative_forward.h"
#include "relative_turning.h"
#include "rolling_basis.h"
#include "triangle.h"

class Strategy : public Action {
   public:
    Strategy(RollingBasis* rb);
    ~Strategy() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;
    void updateCurrentAction();

   private:
    RollingBasis* _rb;
    std::vector<Action*> _actions;
    int _currentActionIndex = 0;
    void initActions();
};
#endif
