#ifndef ACTIONS_RELATIVE_FORWARD_H
#define ACTIONS_RELATIVE_FORWARD_H

#include "action.h"
#include "navigation.h"

// Distance calibration factor (robot does 2.5x distance, so multiply by 0.4)
#define DISTANCE_CALIBRATION_FACTOR 0.4f

class RelativeForward : public Action {
   public:
    RelativeForward(Navigation* nav, const double distance);
    ~RelativeForward() = default;
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
