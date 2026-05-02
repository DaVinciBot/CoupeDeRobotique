#ifndef ACTIONS_RELATIVE_TURNING_H
#define ACTIONS_RELATIVE_TURNING_H

#include "action.h"
#include "navigation.h"

class RelativeTurning : public Action {
   public:
    RelativeTurning(Navigation* nav, double angle);

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    Point _target;
    Navigation* _navigation;
    double _angle;
    unsigned long _startMs = 0;
    unsigned long _lastPrintMs = 0;
    unsigned long _timeoutMs = 15000;
    float _arriveTolRad = 0.05f;
    bool _started = false;
    bool _finished = false;

    float angleErrorRad() const;
};

#endif
