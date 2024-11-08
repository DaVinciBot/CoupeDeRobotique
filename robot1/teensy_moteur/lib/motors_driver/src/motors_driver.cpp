#include <motors_driver.h>
#include <Arduino.h>

Motor::Motor(byte pin_forward, byte pin_backward, byte pin_pwm, byte pin_enca, byte pin_encb, double wheel_unit_tick_cm, byte max_pwm){
    this->pin_forward = pin_forward;
    this->pin_backward = pin_backward;
    
    this->pin_pwm = pin_pwm;   // PWM pin only !
    this->pin_enca = pin_enca; // AttachInterrupt pin only !
    this->pin_encb = pin_encb; // AttachInterrupt pin only !

    this->max_pwm = max_pwm;

    this->wheel_unit_tick_cm = wheel_unit_tick_cm;
}

void Motor::init(){
    pinMode(this->pin_forward, OUTPUT);
    pinMode(this->pin_backward, OUTPUT);
    pinMode(this->pin_pwm, OUTPUT);

    pinMode(this->pin_enca, INPUT);
    pinMode(this->pin_encb, INPUT);
}

void Motor::set_motor(int pwmVal)
{
    int16_t dir = pwmVal > 0 ? 1 : -1;  
    pwmVal = constrain(abs(pwmVal), 0, this->max_pwm);

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


double Motor::delta_time_calculator()
{
    long current_time = micros();
    double delta_time = (current_time - this->prevT) / (1e6); // in seconds
    this->prevT = current_time;
    return delta_time;
}

void Motor::odometer_handle()
{
    long delta_ticks = this->ticks - this->last_ticks;
    this->last_ticks = this->ticks;

    double delta_time = this->delta_time_calculator();

    this->distance += delta_ticks * this->wheel_unit_tick_cm;
    this->speed = delta_ticks * this->wheel_unit_tick_cm / delta_time;
} 

// void Motor::speed_handle(float target_speed)
// {
//     long delta_ticks = this->ticks - this->last_ticks;
//     this->last_ticks = this->ticks;

//     double delta_time = this->delta_time_calculator();
//     this->speed = delta_ticks * this->wheel_unit_tick_cm / delta_time;

//     float u = this->pid.compute(this->speed, target_speed);

//     Serial.println(String("Current speed: ") + String(this->speed) + String(" | Target speed: ") + String(target_speed) + String(" | PWM: ") + String(u));

//     // Set the correct motor commande
//     set_motor(u > 0 ? 1 : -1, fabs(u));
// }
