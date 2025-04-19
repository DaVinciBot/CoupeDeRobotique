#ifndef PID_H
#define PID_H

class PID
{
public:
    PID(float kp, float ki, float kd,
        float dtSeconds = 0.01f);

    float compute(float error);

    void reset();

    void setTunings(float kp, float ki, float kd);

    void setSampleTime(float dtSeconds);

private:
    float _kp, _ki, _kd;
    float _dtSeconds;
    float _integral;
    float _previousError;
    float _outputMin, _outputMax;
};

#endif