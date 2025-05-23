#include "navigation.h"

Navigation::Navigation(RollingBasis *basis)
    : _basis(basis)
{
}

void Navigation::setCommand(const Point &targetPos)
{
    _basis->setCommand(targetPos);
}

void Navigation::update()
{
    _basis->update();
}

bool Navigation::isMoving() const
{
    return _basis->isMoving();
}

void Navigation::stop()
{
    _basis->stop();
}

Point Navigation::getPose() const
{
    return _basis->getPose();
}

float Navigation::getMeasuredLinearSpeed() const
{
    return _basis->getMeasuredLinearSpeedMmPerS();
}

float Navigation::getMeasuredAngularSpeed() const
{
    return _basis->getMeasuredAngularSpeedRadPerS();
}
