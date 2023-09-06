#include <rolling_basis.h>
#include <Arduino.h>
#include <util/atomic.h>

// Properties
Point Rolling_Basis::get_current_position()
{
    Point position;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
    {
        position.x = this->X;
        position.y = this->Y;
        position.theta = this->THETA;
    }
    return position;
}

Ticks Rolling_Basis::get_current_ticks()
{
    Ticks ticks;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
    {
        ticks.left = this->left_motor->ticks;
        ticks.right = this->right_motor->ticks;
    }
    return ticks;
}

// Constructor
Rolling_Basis::Rolling_Basis(unsigned short encoder_resolution, float center_distance, float wheel_diameter)
{
    this->encoder_resolution = encoder_resolution;
    this->center_distance = center_distance;
    this->wheel_diameter = wheel_diameter;
}

// Methods
// Inits function
void Rolling_Basis::init_right_motor(byte enca, byte encb, byte pwm, byte in2, byte in1, float kp, float kd, float ki, float correction_factor = 1.0, byte threshold_pwm_value = 0)
{
    this->right_motor = new Motor(enca, encb, pwm, in2, in1, kp, kd, ki, correction_factor, threshold_pwm_value);
}

void Rolling_Basis::init_left_motor(byte enca, byte encb, byte pwm, byte in2, byte in1, float kp, float kd, float ki, float correction_factor = 1.0, byte threshold_pwm_value = 0)
{
    this->left_motor = new Motor(enca, encb, pwm, in2, in1, kp, kd, ki, correction_factor, threshold_pwm_value);
}

void Rolling_Basis::init_motors()
{
    this->right_motor->init();
    this->left_motor->init();
}

void Rolling_Basis::init_rolling_basis(float x, float y, float theta, long inactive_delay, byte max_pwm)
{
    this->X = x;
    this->Y = y;
    this->THETA = theta;
    this->inactive_delay = inactive_delay; 
    this->max_pwm = max_pwm;
}

// Odometrie function
void Rolling_Basis::odometrie_handle(){
    /* Determine the position of the robot */
    long delta_left  = this->left_motor->ticks - this->left_ticks;
    this->left_ticks = this->left_ticks + delta_left;

    long delta_right  = this->right_motor->ticks - this->right_ticks;
    this->right_ticks = this->right_ticks + delta_right;
    
    float left_move  = delta_left * this->wheel_unit_tick_cm();
    float right_move = delta_right * this->wheel_unit_tick_cm();

    float movement_difference = right_move - left_move;
    float movement_sum = (right_move + left_move) / 2;

    THETA = THETA + (movement_difference / this->center_distance);
    this->X = this->X + (cos(this->THETA) * movement_sum);
    this->Y = this->Y + (sin(this->THETA) * movement_sum);
}

void Rolling_Basis::is_running_update(){
    // Verify if the robot is running or no
    if ((millis() - this->last_running_check) > 10){
        this->last_running_check = millis();
        long delta_right = abs(this->running_check_right - this->right_motor->ticks);
        long delta_left = abs(this->running_check_left - this->left_motor->ticks);

        if((delta_left > 3) || (delta_right > 3))
            this->last_position_update = millis();
        
        this->running_check_right = this->right_motor->ticks;
        this->running_check_left  = this->left_motor->ticks;

        this->IS_RUNNING = ((millis() - this->last_position_update) < abs(this->inactive_delay));
    }
}

// Motors action function
void Rolling_Basis::keep_position(long current_right_ticks, long current_left_ticks) {
    this->right_motor->handle(current_right_ticks, this->max_pwm);
    this->left_motor->handle(current_left_ticks, this->max_pwm);
}

void Rolling_Basis::shutdown_motor()
{
    this->right_motor->set_motor(1, 0);
    this->left_motor->set_motor(1, 0);
}

