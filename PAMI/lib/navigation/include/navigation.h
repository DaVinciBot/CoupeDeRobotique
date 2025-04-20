#ifndef NAVIGATION_H
#define NAVIGATION_H

#include "rolling_basis.h"

class Navigation
{
public:
    Navigation(RollingBasis *basis);

    void setCommand(float linSpeedMmPerS,
                    float angSpeedRadPerS,
                    const Point &targetPos);

    void update();

    bool isMoving() const;

    void stop();

    Point getPose() const;

    float getMeasuredLinearSpeed() const;

    float getMeasuredAngularSpeed() const;

private:
    RollingBasis *_basis;
};

#endif

// TODO: rajouter la couche supérieure de navigation