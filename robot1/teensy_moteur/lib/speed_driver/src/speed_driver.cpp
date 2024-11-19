#include <Arduino.h>
#include <cmath>
#include <speed_driver.h>

// Speed driver generic class
void Speed_Driver::compute_acceleration_profile(Rolling_Basis_Params *rolling_basis_params, long end_ticks)
{
    this->end_ticks = end_ticks;

    // Compute acceleration profile if not already done and distance is not 0
    if (this->acceleration_params.distance != 0.0f && (this->acceleration_params.a == -1.0f || this->acceleration_params.b == -1.0f || this->acceleration_params.c == -1.0f))
    {
        this->acceleration_params.a = this->acceleration_params.offset / this->max_speed;
        this->acceleration_params.b = this->acceleration_params.distance / 2;
        this->acceleration_params.c = logf(((1 - this->acceleration_params.a) / this->acceleration_params.p) - 1.0f) / this->acceleration_params.b;
    }

    // Compute deceleration profile
    if (this->deceleration_params.distance != 0.0f && (this->deceleration_params.a == -1.0f || this->deceleration_params.b == -1.0f || this->deceleration_params.c == -1.0f))
    {
        this->deceleration_params.a = this->deceleration_params.offset / this->max_speed;
        this->deceleration_params.b = this->deceleration_params.distance / 2;
        this->deceleration_params.c = logf(((1 - this->deceleration_params.a) / this->deceleration_params.p) - 1.0f) / this->deceleration_params.b;
    }
}

byte Speed_Driver::compute_local_speed(long ticks, float current_speed, float dt)
{
    float control_signal = pid.compute(current_speed, dt);
    // Convert control signal to speed
    byte speed = static_cast<byte>(control_signal);
    return speed;
}

// Speed driver from distance
Speed_Driver_From_Distance::Speed_Driver_From_Distance(byte max_speed, byte correction_speed, float acceleration_offset, float acceleration_distance, float deceleration_offset, float deceleration_distance)
{
    this->max_speed = max_speed;
    this->correction_speed = correction_speed;

    // Acceleration params
    this->acceleration_params.offset = acceleration_offset;
    this->acceleration_params.distance = acceleration_distance;
    // Fix sigmoid power
    this->acceleration_params.p = 0.01f;

    // Deceleration params
    this->deceleration_params.offset = deceleration_offset;
    this->deceleration_params.distance = deceleration_distance;
    // Fix sigmoid power
    this->deceleration_params.p = 0.01f;
}