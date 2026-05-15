#ifndef ACTIONS_GO_TO_H
#define ACTIONS_GO_TO_H

#include "action.h"
#include "lidar_pami.h"
#include "rolling_basis.h"

class GoTo : public Action {
   public:
    GoTo(RollingBasis* rb, const Point& target,
         lidar_pami* lidar = nullptr,
         uint16_t acsDistanceMm = 75);
    ~GoTo() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    RollingBasis* _rb;
    Point _target;
    bool _started = false;
    bool _finished = false;

    static lidar_pami* _sLidar;
    static uint16_t _sAcsDistance;
    static bool shouldPause();
};

#endif
