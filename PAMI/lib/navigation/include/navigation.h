#ifndef NAVIGATION_H
#define NAVIGATION_H

#include "rolling_basis.h"

class Navigation
{
public:
    Navigation(RollingBasis *basis);

    void setLinearAngularSpeed(float linearMmS, float angularDegS);
    void update();
    bool isBusy() const;
    void stop();
    void getPose(float &x, float &y, float &theta) const;

private:
    RollingBasis *_basis;
};

#endif
