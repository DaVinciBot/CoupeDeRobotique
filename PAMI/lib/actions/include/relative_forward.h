#ifndef ACTIONS_RELATIVE_FORWARD_H
#define ACTIONS_RELATIVE_FORWARD_H

#include "../../../include/config.h"
#include "action.h"
#include "navigation.h"

class RelativeForward : public Action {
   public:
    RelativeForward(Navigation* nav, double distance);

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    static constexpr float DISTANCE_CALIBRATION = DISTANCE_CALIBRATION_FACTOR;

    Point _target;
    Navigation* _navigation;
    double _distance;
    unsigned long _startMs = 0;
    unsigned long _lastPrintMs = 0;
    unsigned long _timeoutMs = 15000;
    float _arriveTolMm = 5.0f;
    bool _started = false;
    bool _finished = false;
};

#endif
