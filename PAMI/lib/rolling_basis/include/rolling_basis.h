#ifndef ROLLING_BASIS_H
#define ROLLING_BASIS_H

#include "navigation.h"

class Rolling_Basis
{
private:
    float _posX;
    float _posY;
    float _theta;

    long _leftEncoderCount;
    long _rightEncoderCount;

    float _pidKp;
    float _pidKi;
    float _pidKd;
    float _pidIntegral;
    float _pidPrevError;

public:
    Rolling_Basis();
    ~Rolling_Basis();

    void init();
    void update();

    void resetOdometry();
    void updateOdometry();

    void setPIDConstants(float Kp, float Ki, float Kd);
    float computePID(float setpoint, float measured);

    // TODO: déplacer les paramètres physiques de la rolling_basis ici et non dans navigation
    // QUESTION: PID ici ?
};

#endif