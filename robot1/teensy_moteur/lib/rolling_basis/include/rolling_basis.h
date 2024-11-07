#include <Arduino.h>
#include <complex_action.h>

class Rolling_Basis {
public :
    // Rolling basis's params
    inline float radius() { return this->center_distance / 2.0; };
    inline float wheel_perimeter() { return this->wheel_diameter * PI; };
    inline float wheel_unit_tick_cm() { return this->wheel_perimeter() / this->encoder_resolution; };
    byte standby_pwm;

    // Properties
    Point get_current_position();
    Ticks get_current_ticks();

    // Rolling basis's motors
    Motor *right_motor;
    Motor *left_motor;

    // Odometrie
    float X = 0.0f;
    float Y = 0.0f;
    float THETA = 0.0f;
    bool IS_RUNNING = false;

    // Inactive check
    long last_running_check = 0L;
    long last_position_update = 0L;
    long running_check_right = 0L;
    long running_check_left = 0L;
    long inactive_delay = 0L;

    // Ticks
    long left_ticks = 0;
    long right_ticks = 0;

    // Rolling basis params
    unsigned short encoder_resolution;
    float center_distance;
    float wheel_diameter;
    
    // Constructor
    Rolling_Basis(unsigned short encoder_resolution, float center_distance, float wheel_diameter);

    // Inits function
    void init_right_motor(byte enca, byte encb, byte pwm, byte in2, byte in1, float kp, float kd, float ki, float correction_factor, byte threshold_pwm_value);
    void init_left_motor(byte enca, byte encb, byte pwm, byte in2, byte in1, float kp, float kd, float ki, float correction_factor, byte threshold_pwm_value);
    void init_motors();
    void init_rolling_basis(float x, float y, float theta, long inactive_delay, byte max_pwm);

    // Odometrie function
    void odometrie_handle();
    void is_running_update();
    void reset_position();

    // Motors action function
    void keep_position(long current_right_ticks, long current_left_ticks);
    void shutdown_motor();
};