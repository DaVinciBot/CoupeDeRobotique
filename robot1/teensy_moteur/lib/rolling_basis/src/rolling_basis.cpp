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

// Constructor
Rolling_Basis::Rolling_Basis(
        unsigned short encoder_resolution, float center_distance, float wheel_diameter, 
        const PID& linear_speed_pid, const PID& angular_speed_pid, const PID& linear_distance_pid, const PID& angular_distance_pid
    )
    : encoder_resolution(encoder_resolution), 
      center_distance(center_distance), 
      wheel_diameter(wheel_diameter), 
      linear_speed_pid(linear_speed_pid), 
      angular_speed_pid(angular_speed_pid), 
      linear_distance_pid(linear_distance_pid), 
      angular_distance_pid(angular_distance_pid)
{}


// Methods
// Inits function
void Rolling_Basis::define_right_motor(byte enca, byte encb, byte pwm, byte in2, byte in1, byte max_pwm)
{
    this->right_motor = new Motor(in1, in2, pwm, enca, encb, this->wheel_unit_tick_cm(), max_pwm);
} 
void Rolling_Basis::define_left_motor(byte enca, byte encb, byte pwm, byte in2, byte in1, byte max_pwm)
{
    this->left_motor = new Motor(in1, in2, pwm, enca, encb, this->wheel_unit_tick_cm(), max_pwm);
}

void Rolling_Basis::init_motors()
{
    this->right_motor->init();
    this->left_motor->init();
}

void Rolling_Basis::init_rolling_basis(float x, float y, float theta)
{
    this->X = x;
    this->Y = y;
    this->THETA = theta;
}

// Odometrie function
void Rolling_Basis::odometrie_handle(){
    /* Save last motors positions */
    double last_right_distance = this->right_motor->distance;
    double last_left_distance  = this->left_motor->distance;

    /* Update motors positions by calling odometer_handle */
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
    {
        this->right_motor->odometer_handle();
        this->left_motor->odometer_handle();
    }

    /* Compute motors deplacement */
    double right_move = this->right_motor->distance - last_right_distance;
    double left_move  = this->left_motor->distance - last_left_distance;

    /* Determine the position of the robot */
    float movement_difference = right_move - left_move;
    float movement_sum = (right_move + left_move) / 2;

    this->THETA = this->THETA - (movement_difference / this->center_distance);
    this->X = this->X + (cos(this->THETA) * movement_sum);
    this->Y = this->Y + (sin(this->THETA) * movement_sum);
}

void Rolling_Basis::handle(
        Point target_position, 
        float target_linear_speed, float target_angular_speed
    ) {
    /* Speed part */
    // Compute real linear and angular speed
    double Vm = (this->right_motor->speed + this->left_motor->speed) / 2; // Vitesse linéaire mesurée
    double Wm = (this->right_motor->speed - this->left_motor->speed) / this->center_distance; // Vitesse angulaire mesurée

    // Save speeds as rolling basis properties
    this->linear_speed  = (float)Vm;
    this->angular_speed = (float)Wm;

    // Compute linear and angular speed error (difference between target and real)
    double Ev = target_linear_speed - Vm;
    double Ew = target_angular_speed - Wm;

    // Compute PID output based on errors
    double linear_speed_correction = this->linear_speed_pid.compute(Ev);
    double angular_speed_correction = this->angular_speed_pid.compute(Ew);


    /* Position part */
    // We already have the current robot's position with odometrie (X, Y, THETA)

    // Compute distance and orientation error (difference between target and real)
    double Ed = sqrt(pow(target_position.x - this->X, 2) + pow(target_position.y - this->Y, 2));
    double Etheta = target_position.theta - fmod(this->THETA, PI); // fmod to keep the angle between -PI and PI, TODO: a tester !!

    // Compute PID output based on errors
    double linear_distance_correction = this->linear_distance_pid.compute(Ed);
    double angular_distance_correction = this->angular_distance_pid.compute(Etheta);

    // Je regarde si le cpp déconne niveau calcul ou pas (sinon c python)
    /*double max_correction = 5.0f;
    linear_speed_correction = constrain(linear_speed_correction, -max_correction, max_correction);
    angular_speed_correction = constrain(angular_speed_correction, -max_correction, max_correction);*/

    /* Combine both corrections */
    // Compute corrected linear and angular speed
    double Vc = target_linear_speed + linear_speed_correction + linear_distance_correction;
    double Wc = target_angular_speed + angular_speed_correction + angular_distance_correction;

    // Compute right and left motor speed 
    double right_speed = (2 * Vc + Wc * this->center_distance) / 2;
    double left_speed = (2 * Vc - Wc * this->center_distance) / 2;

    /*double max_motor_speed = 5.0f;  // On limite a la main la vitesse max pour voir encore qui deconne (moi je pense que c'est le calcul)
    right_speed = constrain(right_speed, -max_motor_speed, max_motor_speed);
    left_speed = constrain(left_speed, -max_motor_speed, max_motor_speed);*/
    
    
    /* Apply commands to motors */
    this->right_motor->set_motor(right_speed);
    this->left_motor->set_motor(left_speed);

    /// LE PRINT INTERDIT AHHHHH (test puis enlever)
    /*Serial.print("Vc: "); Serial.print(Vc);
    Serial.print(" | Wc: "); Serial.print(Wc);
    Serial.print(" | Right Speed: "); Serial.print(right_speed);
    Serial.print(" | Left Speed: "); Serial.println(left_speed);*/

}

// void Rolling_Basis::is_running_update(){
//     // Verify if the robot is running or no
//     if ((millis() - this->last_running_check) > 10){
//         this->last_running_check = millis();
//         long delta_right = abs(this->running_check_right - this->right_motor->ticks);
//         long delta_left = abs(this->running_check_left - this->left_motor->ticks);

//         if((delta_left > 3) || (delta_right > 3))
//             this->last_position_update = millis();
        
//         this->running_check_right = this->right_motor->ticks;
//         this->running_check_left  = this->left_motor->ticks;

//         this->IS_RUNNING = ((millis() - this->last_position_update) < abs(this->inactive_delay));
//     }
// }

// void Rolling_Basis::reset_position(){
//     // Reset the position of the robot
//     this->X = 0.0f;
//     this->Y = 0.0f;
//     this->THETA = 0.0f;
//     this->IS_RUNNING = false;
// }

// // Motors action function
// void Rolling_Basis::keep_position(long current_right_ticks, long current_left_ticks) {
//     this->right_motor->handle(current_right_ticks, this->standby_pwm);
//     this->left_motor->handle(current_left_ticks, this->standby_pwm);
// }

// void Rolling_Basis::shutdown_motor()
// {
//     this->right_motor->set_motor(1, 0);
//     this->left_motor->set_motor(1, 0);
// }
