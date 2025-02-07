#include <pid.h>
#include <Arduino.h>


PID::PID(float kp, float ki, float kd)
{
    this->kp = kp;
    this->kd = kd;
    this->ki = ki;
}

double PID::delta_time_calculator()
{
    long current_time = micros();
    double delta_time = (current_time - this->prevT) / (1e6); // convert to in seconds
    this->prevT = current_time;
    return delta_time;
}

float PID::compute(float error)
{
    double delta_time = this->delta_time_calculator();

    // Calculate derivative
    float dedt = (error - this->error_prev) / delta_time;

    //if (delta_time < 0.001) delta_time = 0.001;  // Évite les valeurs trop petites de delta time comme ca ca deconne moins du moins jespere


    // Calculate integral
    this->error_integral = this->error_integral + (error * delta_time);

    // Control signal
    float u = this->kp * error + this->kd * dedt + this->ki * this->error_integral;

    // Save error
    this->error_prev = error;

    return u;
}