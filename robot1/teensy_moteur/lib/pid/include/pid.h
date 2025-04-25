#include <Arduino.h>

// Motor class
class PID
{
private:
    float error_prev = 0.0f;
    float error_integral = 0.0f;

public:
    // PID constantes
    float kp;
    float ki;
    float kd;

    // Delta Time saver
    long prevT = 0L;
    double delta_time_calculator();

    // Constructor
    PID(float kp, float ki, float kd);

    // Methods
    float compute(float error);
};