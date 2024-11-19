#include <pid.h>

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

    // PID controller
    PID pid;

    Speed_Driver(float kp, float ki, float kd) : pid(kp, ki, kd) {}

    // Methodes
    void compute_acceleration_profile(Rolling_Basis_Params *rolling_basis_params, long end_ticks);
    byte compute_local_speed(long ticks, float current_speed, float dt);
};

class Speed_Driver_From_Distance : public Speed_Driver
{
public:
    Speed_Driver_From_Distance(byte max_speed, byte correction_speed, float acceleration_offset, float acceleration_distance, float deceleration_offset, float deceleration_distance, float kp, float ki, float kd)
        : Speed_Driver(kp, ki, kd) {}
};