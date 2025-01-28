#include <Arduino.h>


// Motor class
class Motor {

private:
    // Pins Motor
    byte pin_forward;
    byte pin_backward;
    byte pin_pwm;  // PWM pin only !
    byte pin_enca; // AttachInterrupt pin only !
    byte pin_encb; // AttachInterrupt pin only !

    byte max_pwm; 

    // Ticks distance
    double wheel_unit_tick_cm;

    // Delta Time saver (used to calculate speed)
    long prevT = 0L;
    double delta_time_calculator();


public:
    volatile long ticks = 0L;

    // Motor description (it is the last data calculated by the motor odometer handle method)
    double distance = 0.0; // Distance in cm 
    double speed = 0.0; // Speed in cm/s 
    long last_ticks = 0L; // Ticks distance used to compute distance and speed (updated at the last odometer handle call)

    // Constructor
    Motor(byte pin_forward, byte pin_backward, byte pin_pwm, byte pin_enca, byte pin_encb, double wheel_unit_tick_cm, byte max_pwm);
    ~Motor() = default;

    // Methods
    void init();
    void set_motor(int pwmVal);
    void odometer_handle();
    // void speed_handle(float target_speed);
    // void handle(long target_pos, byte max_speed);
};