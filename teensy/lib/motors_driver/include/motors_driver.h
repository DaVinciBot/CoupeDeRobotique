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

    // PID constantes
    float kp;
    float kd;
    float ki;

    // Variables
    int error_prev = 0;
    float error_integral = 0;
    
public:
    // Delta Time saver
    long prevT = 0;
    double delta_time_calculator();

    // Position in ticks variable
    volatile long ticks = 0;

    // Correction speed factor
    float correction_factor;
    byte threshold_pwm_value;
    
    // Constructor
    Motor(byte pin_forward, byte pin_backward, byte pin_pwm, byte pin_enca, byte pin_encb, float kp, float kd, float ki, float correction_factor, byte threshold_pwm_value);

    // Methods
    void init();
    void set_motor(int8_t dir, byte pwmVal);
    void handle(long target_pos, byte max_speed);
};