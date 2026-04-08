#ifndef ACTIONS_RELATIVE_BACKWARD_H
#define ACTIONS_RELATIVE_BACKWARD_H

#include "action.h"
#include "navigation.h"

class RelativeBackward : public Action {
   public:
    RelativeBackward(Navigation* nav, const double distance);
    ~RelativeBackward() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    Point _target;
    Navigation* _navigation;
    const double _distance;
    unsigned long _startMs = 0;
    unsigned long _timeoutMs = 15000;  // Ms
    float _arriveTolMm = 5.0f;
    bool _finished = false;
};

#endif
