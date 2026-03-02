#ifndef ACTIONS_ROTATE_ACTION_H
#define ACTIONS_ROTATE_ACTION_H

#include "action.h"
#include "rolling_basis.h"

class RotateAction : public Action {
   public:
    RotateAction(RollingBasis* rb, float durationSec)
        : _rb(rb), _duration(durationSec), _done(false), _startTime(0) {}

    void start() override {
        _done = false;
        _startTime = micros();
        _rb->setSpeed(0.0f, 1.5f);
    }

    void update() override {
        _rb->updateMotors();
        float elapsed = (micros() - _startTime) * 1e-6f;
        if (elapsed >= _duration) {
            _rb->stop();
            _done = true;
        }
    }

    void stop() override { _rb->stop(); }
    bool isFinished() const override { return _done; }
    const char* name() const override { return "RotateAction"; }

   private:
    RollingBasis* _rb;
    float _duration;
    unsigned long _startTime;
    bool _done;
};

#endif