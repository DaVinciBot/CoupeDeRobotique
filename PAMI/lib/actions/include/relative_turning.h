#ifndef ACTIONS_RELATIVE_TURNING_H
#define ACTIONS_RELATIVE_TURNING_H

#include "action.h"
#include "navigation.h"

class RelativeTurning : public Action {
   public:
    RelativeTurning(Navigation* nav, const double angle);
    ~RelativeTurning() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    Point _target;
    Navigation* _navigation;
    const double _angle;
    unsigned long _startMs = 0;
    unsigned long _timeoutMs = 15000;  // Ms
    float _arriveTolRad = 3.0f;
    bool _finished = false;
};

#endif
