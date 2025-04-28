/**
 * This is the implementation of the Rolling Basis class.
 * The Rolling Basis class is the core of the Motor teensy code.
 * It provides method to control the motors, the speed and the orientation.
 * It computes the odometry and correct the motors error with the PID class.
 */

#include <rolling_basis.h>
#include <Arduino.h>
#include <util/atomic.h>

// Properties
/**
 * @brief Get current position (X, Y and THETA) of the robot
 *
 * @return Current position
 */
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
/**
 * @brief constructor of the Rolling Basis class
 *
 * Initializes the parameters of the Rolling Basis
 */
Rolling_Basis::Rolling_Basis(
    unsigned short encoder_resolution, float center_distance, float wheel_diameter,
    const PID &linear_speed_pid, const PID &angular_speed_pid, const PID &linear_distance_pid, const PID &angular_distance_pid)
    : encoder_resolution(encoder_resolution),
      center_distance(center_distance),
      wheel_diameter(wheel_diameter),
      linear_speed_pid(linear_speed_pid),
      angular_speed_pid(angular_speed_pid),
      linear_distance_pid(linear_distance_pid),
      angular_distance_pid(angular_distance_pid)
{
}

// Methods
// Inits function
/**
 * @brief Define right motor with pins, related encoders pin and properties of the wheel attached to the motor.
 */
void Rolling_Basis::define_right_motor(byte enca, byte encb, byte pwm, byte in2, byte in1, byte max_pwm)
{
    this->right_motor = new Motor(in1, in2, pwm, enca, encb, this->wheel_unit_tick_cm(), max_pwm);
}

/**
 * @brief Define left motor with pins, related encoders pin and properties of the wheel attached to the motor.
 */
void Rolling_Basis::define_left_motor(byte enca, byte encb, byte pwm, byte in2, byte in1, byte max_pwm)
{
    this->left_motor = new Motor(in1, in2, pwm, enca, encb, this->wheel_unit_tick_cm(), max_pwm);
}

/**
 * @brief Initialize both motors
 */
void Rolling_Basis::init_motors()
{
    this->right_motor->init();
    this->left_motor->init();
}

/**
 * @brief Initialize Rolling Basis state with starting position
 */
void Rolling_Basis::init_rolling_basis(float x, float y, float theta)
{
    this->X = x;
    this->Y = y;
    this->THETA = theta;
}

// Odometrie function
/**
 * @brief Handle the odometry computation
 *
 * Update motors position sthen compute displacement of both motors.
 * The with these results, estimate the robot position and orientation.
 * Finally update the rolling basis state.
 */
void Rolling_Basis::odometrie_handle()
{
    /* Save last motors positions */
    double last_right_distance = this->right_motor->distance;
    double last_left_distance = this->left_motor->distance;

    /* Update motors positions by calling odometer_handle */
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
    {
        this->right_motor->odometer_handle();
        this->left_motor->odometer_handle();
    }

    /* Compute motors deplacement */
    double right_move = this->right_motor->distance - last_right_distance;
    double left_move = this->left_motor->distance - last_left_distance;

    /* Determine the position of the robot */
    float delta_distance = (right_move + left_move) / 2.0f;
    float delta_theta = (right_move - left_move) / this->center_distance;

    this->THETA = fmod(this->THETA + delta_theta, PI);
    this->X = this->X + (sin(this->THETA) * delta_distance);
    this->Y = this->Y + (cos(this->THETA) * delta_distance);
}

/**
 * @brief Handle the correction computation
 *
 * Compute the distance and orientation error in terms of position.A0
 * Compute the PID and set the motors new command.
 */
void Rolling_Basis::handle(
    Point target_position,
    float target_linear_speed, float target_angular_speed, Com *com)
{
    /* Position part */
    // We already have the current robot's position with odometrie (X, Y, THETA)

    // Compute distance and orientation error (difference between target and real)
    double distance_error = sqrt(pow(target_position.x - this->X, 2) + pow(target_position.y - this->Y, 2));
    double theta_error = target_position.theta - fmod(this->THETA, PI); // fmod to keep the angle between -PI and PI, TODO: a tester !!

    // Compute PID output based on errors
    double linear_distance_correction = this->linear_distance_pid.compute(distance_error);
    double angular_distance_correction = this->angular_distance_pid.compute(theta_error);

    this->right_motor->set_motor(angular_distance_correction + linear_distance_correction);
    this->left_motor->set_motor(angular_distance_correction - linear_distance_correction);
}