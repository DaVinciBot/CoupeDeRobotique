#include <motors_driver.h>
#include <Arduino.h>
#include <util/atomic.h>

Motor::Motor(byte pin_forward, byte pin_backward, byte pin_pwm, byte pin_enca, byte pin_encb, float kp, float kd, float ki, float correction_factor = 1.0, byte threshold_pwm_value=0)
{   
    this->pin_forward = pin_forward;
    this->pin_backward = pin_backward;
    this->pin_pwm = pin_pwm;   // PWM pin only !
    this->pin_enca = pin_enca; // AttachInterrupt pin only !
    this->pin_encb = pin_encb; // AttachInterrupt pin only !

    this->kp = kp;
    this->kd = kd;
    this->ki = ki;

    this->correction_factor = correction_factor;
    this->threshold_pwm_value = threshold_pwm_value;
}

double Motor::delta_time_calculator()
{
    long current_time = micros();
    double delta_time = (current_time - this->prevT) / (1e6);
    this->prevT = current_time;
    return delta_time;
}

void Motor::init(){
    pinMode(this->pin_forward, OUTPUT);
    pinMode(this->pin_backward, OUTPUT);
    pinMode(this->pin_pwm, OUTPUT);

    pinMode(this->pin_enca, INPUT);
    pinMode(this->pin_encb, INPUT);
}

void Motor::set_motor(int8_t dir, byte pwmVal)
{
    analogWrite(this->pin_pwm, pwmVal);
    if (dir == 1)
    {
        digitalWrite(this->pin_forward, HIGH);
        digitalWrite(this->pin_backward, LOW);
    }
    else if (dir == -1)
    {
        digitalWrite(this->pin_forward, LOW);
        digitalWrite(this->pin_backward, HIGH);
    }
    else
    {
        digitalWrite(this->pin_forward, LOW);
        digitalWrite(this->pin_backward, LOW);
    }
}

void Motor::handle(long target_pos, byte max_speed)
{
    long fix_ticks = this->ticks;
    double delta_time = this->delta_time_calculator();

    // Calculate error
    int error = fix_ticks - target_pos;

    // Calculate derivative
    double dedt = (error - this->error_prev) / delta_time;

    // Calculate integral
    this->error_integral = this->error_integral + (error * delta_time);

    // Control signal
    float u = this->kp * error + this->kd * dedt + this->ki * this->error_integral;

    // Motor power
    float power = fabs(u * this->correction_factor);
    if (power > max_speed * this->correction_factor)
        power = max_speed;

    // Increase power (to overcome friction)
    power += this->threshold_pwm_value;
    if(power > 255) power = 255;

    // Motor direction
    int8_t direction = 1;
    if (u < 0)
        direction = -1;

    // Set the correct motor commande
    set_motor(direction, power);

    // Save error
    this->error_prev = error;
}

