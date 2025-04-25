#include <Arduino.h>
#include <pid.h>
#include <motors_driver.h>
#include "structures.h"

#include <com.h>           // Communication object to manage the communication between the teensy and the Raspberry Pi


class Rolling_Basis {
public :
    // PID controllers
    PID linear_speed_pid;
    PID angular_speed_pid;

    PID linear_distance_pid;
    PID angular_distance_pid;

    // Rolling basis's params
    inline float radius() { return this->center_distance / 2.0; };
    inline float wheel_perimeter() { return this->wheel_diameter * PI; };
    inline float wheel_unit_tick_cm() { return this->wheel_perimeter() / this->encoder_resolution; };

    // Properties
    Point get_current_position();

    // Rolling basis's motors
    Motor *right_motor;
    Motor *left_motor;

    // Odometrie
    float X = 0.0f;
    float Y = 0.0f;
    float THETA = 0.0f;

    float linear_speed = 0.0f;
    float angular_speed = 0.0f;

    // Rolling basis params
    unsigned short encoder_resolution;
    float center_distance;
    float wheel_diameter;
    
    // Constructor
    Rolling_Basis(
        unsigned short encoder_resolution, float center_distance, float wheel_diameter, 
        const PID& linear_speed_pid, const PID& angular_speed_pid, const PID& linear_distance_pid, const PID& angular_distance_pid
    );
    ~Rolling_Basis() = default;

    // Inits function
    void define_right_motor(byte enca, byte encb, byte pwm, byte in2, byte in1, byte max_pwm);
    void define_left_motor( byte enca, byte encb, byte pwm, byte in2, byte in1, byte max_pwm);
    void init_motors();
    void init_rolling_basis(float x, float y, float theta);

    // Odometrie function
    void odometrie_handle();
    void handle(
        Point target_position, 
        float target_linear_speed, float target_angular_speed, Com* com
    );

    // Motors action function
    // void keep_position(long current_right_ticks, long current_left_ticks);
    // void shutdown_motor();
};