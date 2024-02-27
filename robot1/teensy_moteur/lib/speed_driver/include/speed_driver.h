#include <Arduino.h>
#include <motors_driver.h>
#include <structures.h>

class Speed_Driver
{
    // How to use speed Driver:
    // Give gamma and offset
    // 2 cases:
    // 1°) Give Gamma value, it will be directly use to compute the speed (use Speed_Driver_From_Gamma class)
    // speed = gamma * ticks + offset (speed <= max_speed)
    // 2°) Give distance_to_max_speed, it will be use to compute gamma (use Speed_Driver_From_Distance class)
    // The distance_to_max_speed has to be given in cm, when the compute function will be
    // called, the encoder_resolution and wheel_perimeter will be used to convert it in ticks
    // Gamma = (max_speed - offset) / (distance_to_max_speed * encoder_resoltion / wheel_perimeter)
public:
    // Attributes
    byte max_speed;
    byte correction_speed;
    long end_ticks;
    bool next_move_correction = false;

    // Acceleration params
    Profil_params acceleration_params = {0, -1.0f, -1.0f};

    // Deceleration params
    Profil_params deceleration_params = {0, -1.0f, -1.0f};

    Speed_Driver() = default;

    // Methodes
    void compute_acceleration_profile(Rolling_Basis_Params *rolling_basis_params, long end_ticks);
    byte compute_local_speed(long ticks);
};

class Speed_Driver_From_Gamma : public Speed_Driver
{
public:
    // We only need to give gamma and offset, the distance is not used in this case (it's set to -1.0f by default and will be ingored if given)
    Speed_Driver_From_Gamma(byte max_speed, byte correction_speed, Profil_params acceleration, Profil_params deceleration);
};

class Speed_Driver_From_Distance : public Speed_Driver
{
public:
    // We only need to give distance and offset, the gamma is not used in this case (it's set to -1.0f by default and will be ingored if given)
    Speed_Driver_From_Distance(byte max_speed, byte correction_speed, Profil_params acceleration, Profil_params deceleration);
};
