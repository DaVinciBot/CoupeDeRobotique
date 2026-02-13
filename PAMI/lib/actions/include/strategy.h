#ifndef STRATEGY_H 
#define STRATEGY_H 
#include "action.h"
#include "rolling_basis.h" 
#include "AtoB.h" 
#include "relative_forward.h" 
#include "relative_turning.h" 
#include "carre.h" 
#include "triangle.h" 
#include "actionneur.h" 

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
    Action* _actions[10];
    int _currentActionIndex = 0;
    int _actionCount = 0;
    void initActions();

};
#endif