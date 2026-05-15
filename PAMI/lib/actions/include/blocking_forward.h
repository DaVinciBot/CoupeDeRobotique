#ifndef ACTIONS_BLOCKING_FORWARD_H
#define ACTIONS_BLOCKING_FORWARD_H

#include "action.h"
#include "lidar_pami.h"
#include "rolling_basis.h"

class BlockingForward : public Action {
   public:
    BlockingForward(RollingBasis* rb, float distanceMm,
                    lidar_pami* lidar = nullptr,
                    uint16_t acsDistanceMm = 75);

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    RollingBasis* _rb;
    float _distanceMm;
    bool _started = false;
    bool _finished = false;

    static lidar_pami* _sLidar;
    static uint16_t _sAcsDistance;
    static bool shouldPause();
};

#endif
