#ifndef NAVIGATION_H
#define NAVIGATION_H

#include <vector>
#include "rolling_basis.h"

class Navigation {
   public:
    // timeoutMs: maximum run time before forced stop
    Navigation(RollingBasis* basis, uint32_t timeoutMs);

    void setCommand(const Point& targetPos);

    void update();

    bool isMoving() const;

    void stop();

    Point getPose() const;

    float getMeasuredLinearSpeed() const;

    float getMeasuredAngularSpeed() const;

   private:
    RollingBasis* _basis;
    uint32_t _sendIntervalMs;
    uint32_t _timeoutMs;
    uint32_t _lastSendMs;
    uint32_t _startMs;
    Point _lastTarget;

    // nouveaux champs pour découper le trajet
    std::vector<Point> _waypoints;
    size_t _wpIndex;
    static constexpr size_t DEFAULT_SEGMENTS = 1;
};

#endif

// TODO: rajouter la couche supérieure de navigation
