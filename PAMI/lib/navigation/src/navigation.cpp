#include "navigation.h"

Navigation::Navigation(RollingBasis *basis)
    : _basis(basis)
{
}

void Navigation::setLinearAngularSpeed(float linearMmS, float angularDegS)
{
    _basis->setLinearAngularSpeed(linearMmS, angularDegS);
}

void Navigation::update()
{
    _basis->update();
}

bool Navigation::isBusy() const
{
    return _basis->isMoving();
}

void Navigation::stop()
{
    _basis->stop();
}

void Navigation::getPose(float &x, float &y, float &theta) const
{
    _basis->getPose(x, y, theta);
}
