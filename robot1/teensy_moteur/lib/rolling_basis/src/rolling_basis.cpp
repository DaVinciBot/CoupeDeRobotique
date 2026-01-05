/**
 * This is the implementation of the Rolling Basis class.
 * The Rolling Basis class is the core of the Motor teensy code.
 * It provides method to control the motors, the speed and the orientation.
 * It computes the odometry and correct the motors error with the PID class.
 */

#include <Arduino.h>
#include <rolling_basis.h>
#include <util/atomic.h>

double normalizeAngle(double theta) {
    // shift by +PI, take modulo 2*PI, remap to [0,2*PI)
    theta = fmodf(theta + PI, 2.0f * PI);
    if (theta < 0.0f) {
        theta += 2.0f * PI;
    }
    // shift back to [-PI, +PI)
    return theta - PI;
}

// Properties
/**
 * @brief Get current position (X, Y and THETA) of the robot
 *
 * @return Current position
 */
Point Rolling_Basis::get_current_position() {
    Point position;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        position.x = this->X;
        position.y = this->Y;
        position.theta = this->THETA;
    }
    return position;
}

// Constructor
/**
 * @brief Constructor of the Rolling Basis class
 *
 * Initializes the parameters of the Rolling Basis
 */
Rolling_Basis::Rolling_Basis(unsigned short encoder_resolution,
                             double center_distance,
                             double wheel_diameter,
                             const PID& linear_velocity_pid,
                             const PID& angular_velocity_pid)
    : encoder_resolution(encoder_resolution),
      center_distance(center_distance),
      wheel_diameter(wheel_diameter),
      linear_velocity_pid(linear_velocity_pid),
      angular_velocity_pid(angular_velocity_pid) {}

// Methods
// Inits function
/**
 * @brief Define right motor with pins, related encoders pin and properties of
 * the wheel attached to the motor.
 */
void Rolling_Basis::define_right_motor(byte enca,
                                       byte encb,
                                       byte pwm,
                                       byte in2,
                                       byte in1,
                                       byte max_pwm) {
    this->right_motor = new Motor(in1, in2, pwm, enca, encb,
                                  this->wheel_unit_tick_cm(), max_pwm);
}

/**
 * @brief Define left motor with pins, related encoders pin and properties of
 * the wheel attached to the motor.
 */
void Rolling_Basis::define_left_motor(byte enca,
                                      byte encb,
                                      byte pwm,
                                      byte in2,
                                      byte in1,
                                      byte max_pwm) {
    this->left_motor = new Motor(in1, in2, pwm, enca, encb,
                                 this->wheel_unit_tick_cm(), max_pwm);
}

/**
 * @brief Initialize both motors
 */
void Rolling_Basis::init_motors() {
    this->right_motor->init();
    this->left_motor->init();
}

/**
 * @brief Initialize Rolling Basis state with starting position
 */
void Rolling_Basis::init_rolling_basis(double x, double y, double theta) {
    this->X = x;
    this->Y = y;
    this->THETA = theta;
    this->linear_velocity = 0.0f;
    this->angular_velocity = 0.0f;
    this->last_odometrie_time = micros();
}

// Odometrie function
/**
 * @brief Handle the odometry computation
 *
 * Update motors position sthen compute displacement of both motors.
 * The with these results, estimate the robot position and orientation.
 * Finally update the rolling basis state.
 */
void Rolling_Basis::odometrie_handle() {
    unsigned long now = micros();
    double dt = 0.0;
    if (this->last_odometrie_time != 0UL) {
        dt = (now - this->last_odometrie_time) * 1e-6;
    }
    this->last_odometrie_time = now;

    /* Update motors positions by calling odometer_handle */
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        this->right_motor->handle_odometrie();
        this->left_motor->handle_odometrie();
    }

    /* Determine the delta of distance and rotation of the robot */
    double delta_distance =
        (this->left_motor->distance + this->right_motor->distance) / 2.0f;
    double delta_theta =
        (this->right_motor->distance - this->left_motor->distance) /
        this->center_distance;

    // Determine the new cartesian position of the robot
    this->X += cosf(this->THETA + (delta_theta / 2.0f)) * delta_distance;
    this->Y += sinf(this->THETA + (delta_theta / 2.0f)) * delta_distance;
    this->THETA = normalizeAngle(this->THETA + delta_theta);

    if (dt > 0.0) {
        this->linear_velocity = delta_distance / dt;
        this->angular_velocity = delta_theta / dt;
    }
}

/**
 * @brief Handle the correction computation
 *
 * Compute the linear and angular velocity error then apply PID and set
 * the motors new command.
 */
void Rolling_Basis::handle(const VelocityCommand& target_velocity) {
    double linear_error = target_velocity.linear - this->linear_velocity;
    double angular_error = target_velocity.angular - this->angular_velocity;

    double linear_correction = this->linear_velocity_pid.compute(linear_error);
    double angular_correction =
        this->angular_velocity_pid.compute(angular_error);

    double linear_ff = target_velocity.linear;
    double angular_ff = target_velocity.angular;

    double linear_cmd = linear_correction + linear_ff;
    double angular_cmd = angular_correction + angular_ff;

    this->last_linear_error = linear_error;
    this->last_angular_error = angular_error;
    this->last_linear_correction = linear_cmd;
    this->last_angular_correction = angular_cmd;

    double right_pwm = linear_cmd + angular_cmd;
    double left_pwm = linear_cmd - angular_cmd;

    this->right_motor->set_motor(right_pwm);
    this->left_motor->set_motor(left_pwm);
}
