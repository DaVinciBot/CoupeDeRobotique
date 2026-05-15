#ifndef ACTIONS_BLOCKING_TURN_H
#define ACTIONS_BLOCKING_TURN_H

#include "action.h"
#include "lidar_pami.h"
#include "rolling_basis.h"

class BlockingTurn : public Action {
   public:
    BlockingTurn(RollingBasis* rb, float angleRad,
                 lidar_pami* lidar = nullptr,
                 uint16_t acsDistanceMm = 75);

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    RollingBasis* _rb;
    float _angleRad;
    bool _started = false;
    bool _finished = false;

    static lidar_pami* _sLidar;
    static uint16_t _sAcsDistance;
    static bool shouldPause();
};

#endif
