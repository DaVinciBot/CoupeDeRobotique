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
 * @brief constructor of the Rolling Basis class
 *
 * Initializes the parameters of the Rolling Basis
 */
Rolling_Basis::Rolling_Basis(unsigned short encoder_resolution,
                             double center_distance,
                             double wheel_diameter,
                             const PID& linear_distance_pid,
                             const PID& angular_distance_pid)
    : encoder_resolution(encoder_resolution),
      center_distance(center_distance),
      wheel_diameter(wheel_diameter),
      linear_distance_pid(linear_distance_pid),
      angular_distance_pid(angular_distance_pid) {}

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
    /* Update motors positions by calling odometer_handle */
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        this->right_motor->handle_odometrie();
        this->left_motor->handle_odometrie();
    }

    /* Determine the delta of distance and rotation of the robot */
    double delta_distance =
        (this->left_motor->distance + this->right_motor->distance) / 2.0f;
    double delta_theta =
        (this->left_motor->distance - this->right_motor->distance) /
        this->center_distance;

    // Determine the new cartesian position of the robot
    this->X += cosf(this->THETA + (delta_theta / 2.0f)) * delta_distance;
    this->Y += sinf(this->THETA + (delta_theta / 2.0f)) * delta_distance;
    this->THETA = normalizeAngle(this->THETA + delta_theta);
}

/**
 * @brief Handle the correction computation
 *
 * Compute the distance and orientation error in terms of position.A0
 * Compute the PID and set the motors new command.
 */
void Rolling_Basis::handle(Point target_position, Com* com) {
    /* Position part */
    // We already have the current robot's position with odometrie (X, Y, THETA)

    // Compute distance and orientation error (difference between target and
    // real)
    double xerr = target_position.x - this->X;
    double yerr = target_position.y - this->Y;

    double distance_error = xerr * cosf(this->THETA) + yerr * sinf(this->THETA);
    double mag = sqrt(pow(xerr, 2) + pow(yerr, 2));
    double sign = (distance_error >= 0.0) ? +1.0 : -1.0;
    distance_error = mag * sign;

    double theta_error = target_position.theta - this->THETA;
    /*+ Point::angle(
        Point(this->X, this->Y, this->THETA),
        target_position
    ) - this->THETA;*/

    theta_error = normalizeAngle(theta_error);

    // Consigne vitesse
    // Compute PID output based on errors
    double linear_correction =
        this->linear_distance_pid.compute(distance_error);
    double angular_correction = this->angular_distance_pid.compute(theta_error);

    double right_pwm = linear_correction - angular_correction;
    double left_pwm = linear_correction + angular_correction;

    // static long ticks_counter = 0;
    // if (ticks_counter++ > 10) {
    //     ticks_counter = 0;
    //     String pwms = "PWMs: " + String(right_pwm) + ", " + String(left_pwm);
    //     com->print((char *)pwms.c_str());
    // }

    this->right_motor->set_motor(right_pwm);
    this->left_motor->set_motor(left_pwm);
}
