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
    /* Update motors positions by calling odometer_handle */
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
    {
        this->right_motor->update_odometer();
        this->left_motor->update_odometer();
    }

    /* Determine the delta of distance and rotation of the robot */
    float delta_distance = (this->right_motor->distance + this->left_motor->distance) / 2.0f;
    float delta_theta = (this->left_motor->distance - this->right_motor->distance) / this->center_distance;

    // Determine the new cartesian position of the robot
    this->THETA = fmod(this->THETA + delta_theta, 2 * PI);
    this->X = this->X + (cosf(this->THETA) * delta_distance);
    this->Y = this->Y + (sinf(this->THETA) * delta_distance);
    if (this->THETA > PI)
    {
        this->THETA -= 2 * PI;
    }
    else if (this->THETA < -PI)
    {
        this->THETA += 2 * PI;
    }
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
    double xerr = target_position.x - this->X;
    double yerr = target_position.y - this->Y;
    double distance_error = sqrt(pow(xerr, 2) + pow(yerr, 2));
    double theta_error_odometry = target_position.theta - fmod(this->THETA, 2 * PI); // fmod to keep the angle between -PI and PI, TODO: a tester !!
    double orientation_error = fmod(atan2(yerr, xerr) - theta_error_odometry, 2 * PI) * 2.0;
    if (orientation_error > PI)
    {
        orientation_error -= 2 * PI;
    }
    else if (orientation_error < -PI)
    {
        orientation_error += 2 * PI;
    }

    double theta_error = 180.0 * orientation_error / PI;

    // Consigne vitesse

    // Compute PID output based on errors
    double linear_distance_correction = this->linear_distance_pid.compute(distance_error);
    double angular_distance_correction = this->angular_distance_pid.compute(theta_error * 2.0);

    // Compute PID with derived output control
    // double distance_output = sqrt(pow(this->X, 2) + pow(this->Y, 2));
    // double orientation_output = fmod(atan2(this->Y, this->Y) - this->THETA, PI);
    // linear_distance_correction = this->linear_distance_pid.compute_derived_output_control(distance_error, distance_output);
    // angular_distance_correction = this->angular_distance_pid.compute_derived_output_control(orientation_error, orientation_output);

    this->right_motor->set_motor(linear_distance_correction - angular_distance_correction);
    this->left_motor->set_motor(angular_distance_correction + linear_distance_correction);
    double pwmRight = angular_distance_correction + linear_distance_correction;
    double pwmLeft = angular_distance_correction + linear_distance_correction;
    String error = "Angular error : " + String(theta_error) + "Linear error: " + String(distance_error);
    String pwm = "PWM Right: " + String(pwmRight) + " PWM Left: " + String(pwmLeft);
    com->print((char *)pwm.c_str());
    com->print((char *)error.c_str());
}