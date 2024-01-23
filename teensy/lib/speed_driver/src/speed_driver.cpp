#include <speed_driver.h>
#include <Arduino.h>

// Speed driver generic class
void Speed_Driver::compute_acceleration_profile(Rolling_Basis_Params *rolling_basis_params, long end_ticks)
{
    this->end_ticks = end_ticks;

    // Compute acceleration profile
    if (this->acceleration_params.gamma == -1.0f)
    {
        byte y_delta = this->max_speed - this->acceleration_params.offset;
        float distance_to_max_speed_ticks = (this->acceleration_params.distance * rolling_basis_params->encoder_resolution) / rolling_basis_params->wheel_perimeter;
        this->acceleration_params.gamma = (float)y_delta / distance_to_max_speed_ticks;
    }

    // Compute deceleration profile
    if (this->deceleration_params.gamma == -1.0f)
    {
        byte y_delta = this->max_speed - this->deceleration_params.offset;
        float distance_to_speed_down_ticks = this->end_ticks - (this->deceleration_params.distance * rolling_basis_params->encoder_resolution) / rolling_basis_params->wheel_perimeter;
        this->deceleration_params.gamma = (float)y_delta / distance_to_speed_down_ticks;
    }
}

byte Speed_Driver::compute_local_speed(long ticks)
{
    // Calculation of speed change points (acceleration -> plateau -> deceleration)
    long start_ceiling_ticks = (this->max_speed - this->acceleration_params.offset) / this->acceleration_params.gamma;
    long end_ceiling_ticks = ((this->max_speed - this->deceleration_params.offset) / this->deceleration_params.gamma) + this->end_ticks;

    byte speed = 0;

    // Check if there is a ceiling
    if (start_ceiling_ticks < end_ceiling_ticks)
    {
        // We are in the acceleration phase
        if (ticks < start_ceiling_ticks)
            speed = (byte)(this->acceleration_params.gamma * ticks + this->acceleration_params.offset);

        // We are in the plateau phase
        else if (ticks < end_ceiling_ticks)
            speed = this->max_speed;

        // We are in the deceleration phase
        else
            speed = (byte)(this->deceleration_params.gamma * (ticks - this->end_ticks) + this->deceleration_params.offset);
    }
    // No ceiling
    else
    {
        // Calculate the intersection point between the acceleration and deceleration trajectories
        long intersection_ticks = (this->deceleration_params.offset - this->acceleration_params.offset - (this->deceleration_params.gamma * this->end_ticks)) / (this->acceleration_params.gamma - this->deceleration_params.gamma);

        // phase acceleration
        if (ticks < intersection_ticks)
            speed = (byte)(this->acceleration_params.gamma * ticks + this->acceleration_params.offset);

        // phase deceleration
        else
            speed = (byte)(this->deceleration_params.gamma * (ticks - this->end_ticks) + this->deceleration_params.offset);
    }

    // Reduce speed is the next move is a correction
    if (this->next_move_correction)
    {
        this->next_move_correction = false;
        return this->correction_speed;
    }
    
    return speed;
}

// Speed driver from gamma
Speed_Driver_From_Gamma::Speed_Driver_From_Gamma(byte max_speed, byte correction_speed, Profil_params acceleration, Profil_params deceleration)
{
    this->max_speed = max_speed;
    this->correction_speed = correction_speed;

    // Acceleration params
    this->acceleration_params.offset = acceleration.offset;
    this->acceleration_params.gamma = acceleration.gamma;

    // Deceleration params
    this->deceleration_params.offset = deceleration.offset;
    this->deceleration_params.gamma = deceleration.gamma;
}

// Speed driver from distance
Speed_Driver_From_Distance::Speed_Driver_From_Distance(byte max_speed, byte correction_speed, Profil_params acceleration, Profil_params deceleration)
{
    this->max_speed = max_speed;
    this->correction_speed = correction_speed;

    // Acceleration params
    this->acceleration_params.offset = acceleration.offset;
    this->acceleration_params.distance = acceleration.distance;

    // Deceleration params
    this->deceleration_params.offset = deceleration.offset;
    this->deceleration_params.distance = deceleration.distance;
}