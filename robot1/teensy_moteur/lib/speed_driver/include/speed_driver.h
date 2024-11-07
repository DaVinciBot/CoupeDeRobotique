#include <Arduino.h>
#include <motors_driver.h>
#include <structures.h>

class Speed_Driver
{
public:
    // Attributes
    byte max_speed;
    byte correction_speed;
    long end_ticks;
    bool next_move_correction = false;

byte offset;
    float distance;

    // Acceleration params
    Profil_params acceleration_params = {0, -1.0f, -1.0f, -1.0f, -1.0f};

    // Deceleration params
    Profil_params deceleration_params = {0, -1.0f, -1.0f, -1.0f, -1.0f};

    Speed_Driver() = default;

    // Methodes
    void compute_acceleration_profile(Rolling_Basis_Params *rolling_basis_params, long end_ticks);
    byte compute_local_speed(long ticks);
};

class Speed_Driver_From_Distance : public Speed_Driver
{
public:
    // We only need to give distance and offset, the gamma is not used in this case (it's set to -1.0f by default and will be ingored if given)
    Speed_Driver_From_Distance(byte max_speed, byte correction_speed, float acceleration_offset, float acceleration_distance, float deceleration_offset, float deceleration_distance);
};
