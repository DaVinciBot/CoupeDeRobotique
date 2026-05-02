#ifndef ACTIONS_RELATIVE_BACKWARD_H
#define ACTIONS_RELATIVE_BACKWARD_H

#include "action.h"
#include "navigation.h"

class RelativeBackward : public Action {
   public:
    RelativeBackward(Navigation* nav, double distance);

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    static constexpr float DISTANCE_CALIBRATION = 0.4f;

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
