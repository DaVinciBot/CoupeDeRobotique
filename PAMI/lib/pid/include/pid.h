#ifndef PID_H
#define PID_H

#include <limits>

class PID
{
public:
    PID(float kp, float ki, float kd,
        float dtSeconds = 0.01f,
        float outputMin = -std::numeric_limits<float>::infinity(),
        float outpputMax = -std::numeric_limits<float>::infinity());

    float compute(float error);

    void reset();

    void setTunings(float kp, float ki, float kd);

    void setOutputLimits(float min, float max);

    void setSampleTime(float dtSeconds);

private:
    float _kp, _ki, _kd;
    float _dtSeconds;
    float _integral;
    float _previousError;
    float _outputMin, _outputMax;
};

#endif