/**
 * This is the implementation of the Rolling Basis class.
 * The Rolling Basis class is the core of the Motor teensy code.
 * It provides methods to control the motors from pose errors.
 * It computes the odometry and correct the motors error with the PID class.
 */

#include <Arduino.h>
#include <rolling_basis.h>
#include <util/atomic.h>
#include <cmath>

#define MAX_PWM 240

#define POSITION_MAX_LINEAR_STEP_CM 0.8
#define POSITION_MAX_ANGULAR_STEP_CM 0.8

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
                             double left_wheel_diameter,
                             double right_wheel_diameter,
                             const PID& linear_position_pid,
                             const PID& angular_position_pid,
                             const PID& left_wheel_position_pid,
                             const PID& right_wheel_position_pid)
    : encoder_resolution(encoder_resolution),
      center_distance(center_distance),
      left_wheel_diameter(left_wheel_diameter),
      right_wheel_diameter(right_wheel_diameter),
      linear_position_pid(linear_position_pid),
      angular_position_pid(angular_position_pid),
      left_wheel_position_pid(left_wheel_position_pid),
      right_wheel_position_pid(right_wheel_position_pid) {}

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
                                  this->right_wheel_unit_tick_cm(), max_pwm);
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
                                 this->left_wheel_unit_tick_cm(), max_pwm);
}

/**
 * @brief Initialize both motors
 */
void Rolling_Basis::init_motors() {
    this->right_motor->init();
    this->left_motor->init();
    this->right_motor->set_motor(0);
    this->left_motor->set_motor(0);
}

/**
 * @brief Initialize Rolling Basis state with starting position
 */
void Rolling_Basis::init_rolling_basis(double x, double y, double theta) {
    this->X = x;
    this->Y = y;
    this->THETA = theta;
    this->last_linear_error = 0.0;
    this->last_angular_error = 0.0;
    this->last_linear_correction = 0.0;
    this->last_angular_correction = 0.0;
    this->last_left_wheel_error = 0.0;
    this->last_right_wheel_error = 0.0;
    this->left_wheel_target_cm = 0.0;
    this->right_wheel_target_cm = 0.0;
    this->manual_pwm_active = false;
    this->manual_left_pwm = 0;
    this->manual_right_pwm = 0;
    this->manual_pwm_until_ms = 0;
    this->last_odometrie_time = micros();
    if (this->right_motor != nullptr) {
        this->right_motor->ticks = 0L;
        this->right_motor->last_ticks = 0L;
        this->right_motor->last_delta_ticks = 0L;
        this->right_motor->distance = 0.0;
        this->right_motor->set_motor(0);
    }
    if (this->left_motor != nullptr) {
        this->left_motor->ticks = 0L;
        this->left_motor->last_ticks = 0L;
        this->left_motor->last_delta_ticks = 0L;
        this->left_motor->distance = 0.0;
        this->left_motor->set_motor(0);
    }
    this->linear_position_pid.reset();
    this->angular_position_pid.reset();
    this->left_wheel_position_pid.reset();
    this->right_wheel_position_pid.reset();
    this->target_position = Point(x, y, theta);
}

void Rolling_Basis::set_target_position(const Point& position) {
    this->target_position = position;
}

void Rolling_Basis::set_motors_pwm(int16_t left_pwm,
                                   int16_t right_pwm,
                                   uint32_t duration_ms) {
    this->manual_left_pwm = constrain(left_pwm, -MAX_PWM, MAX_PWM);
    this->manual_right_pwm = constrain(right_pwm, -MAX_PWM, MAX_PWM);
    this->manual_pwm_until_ms = millis() + duration_ms;
    this->manual_pwm_active = duration_ms > 0 &&
                              (this->manual_left_pwm != 0 ||
                               this->manual_right_pwm != 0);

    if (!this->manual_pwm_active) {
        this->left_motor->set_motor(0);
        this->right_motor->set_motor(0);
        this->target_position = Point(this->X, this->Y, this->THETA);
        this->left_wheel_target_cm =
            static_cast<double>(this->left_motor->ticks) *
            this->left_wheel_unit_tick_cm();
        this->right_wheel_target_cm =
            static_cast<double>(this->right_motor->ticks) *
            this->right_wheel_unit_tick_cm();
        this->linear_position_pid.reset();
        this->angular_position_pid.reset();
        this->left_wheel_position_pid.reset();
        this->right_wheel_position_pid.reset();
    }
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
    this->last_odometrie_time = micros();

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
}

/**
 * @brief Handle the correction computation
 *
 * Compute the linear/angular position error, update wheel position targets,
 * then let each wheel PID command its motor.
 */
void Rolling_Basis::handle() {
    if (this->manual_pwm_active) {
        if (millis() < this->manual_pwm_until_ms) {
            this->last_linear_error = 0.0;
            this->last_angular_error = 0.0;
            this->last_linear_correction = 0.0;
            this->last_angular_correction = 0.0;
            this->last_left_wheel_error = 0.0;
            this->last_right_wheel_error = 0.0;
            this->left_motor->set_motor(this->manual_left_pwm);
            this->right_motor->set_motor(this->manual_right_pwm);
            return;
        }

        this->manual_pwm_active = false;
        this->manual_left_pwm = 0;
        this->manual_right_pwm = 0;
        this->left_motor->set_motor(0);
        this->right_motor->set_motor(0);
        this->target_position = Point(this->X, this->Y, this->THETA);
        this->left_wheel_target_cm =
            static_cast<double>(this->left_motor->ticks) *
            this->left_wheel_unit_tick_cm();
        this->right_wheel_target_cm =
            static_cast<double>(this->right_motor->ticks) *
            this->right_wheel_unit_tick_cm();
        this->linear_position_pid.reset();
        this->angular_position_pid.reset();
        this->left_wheel_position_pid.reset();
        this->right_wheel_position_pid.reset();
        return;
    }

    double dx = this->target_position.x - this->X;
    double dy = this->target_position.y - this->Y;
    double cos_th = cosf(this->THETA);
    double sin_th = sinf(this->THETA);
    double linear_error = cos_th * dx + sin_th * dy;
    double angular_error =
        normalizeAngle(this->target_position.theta - this->THETA);

    double linear_step = this->linear_position_pid.compute(linear_error);
    double angular_step = this->angular_position_pid.compute(angular_error);

    linear_step = constrain(linear_step, -POSITION_MAX_LINEAR_STEP_CM,
                            POSITION_MAX_LINEAR_STEP_CM);
    angular_step = constrain(angular_step, -POSITION_MAX_ANGULAR_STEP_CM,
                             POSITION_MAX_ANGULAR_STEP_CM);

    this->left_wheel_target_cm += linear_step - angular_step;
    this->right_wheel_target_cm += linear_step + angular_step;

    double left_distance_cm = static_cast<double>(this->left_motor->ticks) *
                              this->left_wheel_unit_tick_cm();
    double right_distance_cm = static_cast<double>(this->right_motor->ticks) *
                               this->right_wheel_unit_tick_cm();
    double left_wheel_error = this->left_wheel_target_cm - left_distance_cm;
    double right_wheel_error = this->right_wheel_target_cm - right_distance_cm;

    double left_pwm = this->left_wheel_position_pid.compute(left_wheel_error);
    double right_pwm =
        this->right_wheel_position_pid.compute(right_wheel_error);

    left_pwm = constrain(left_pwm, -MAX_PWM, MAX_PWM);
    right_pwm = constrain(right_pwm, -MAX_PWM, MAX_PWM);

    this->last_linear_error = linear_error;
    this->last_angular_error = angular_error;
    this->last_linear_correction = linear_step;
    this->last_angular_correction = angular_step;
    this->last_left_wheel_error = left_wheel_error;
    this->last_right_wheel_error = right_wheel_error;

    this->right_motor->set_motor(right_pwm);
    this->left_motor->set_motor(left_pwm);
}
