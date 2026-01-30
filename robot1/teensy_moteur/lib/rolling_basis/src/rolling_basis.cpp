/**
 * This is the implementation of the Rolling Basis class.
 * The Rolling Basis class is the core of the Motor teensy code.
 * It provides method to control the motors, the speed and the orientation.
 * It computes the odometry and correct the motors error with the PID class.
 */

#include <Arduino.h>
#include <rolling_basis.h>
#include <util/atomic.h>
#include <cmath>

#define M_S_TO_CM_S 100.0

#define COMMAND_TIMEOUT_US 100000
#define LINEAR_VELOCITY_ZERO_EPS 0.5
#define ANGULAR_VELOCITY_ZERO_EPS 0.02

#define MIN_PWM_LINEAR 30
#define MIN_PWM_ANGULAR 60
#define LINEAR_FF_PWM_PER_CM_S 6.0
#define ANGULAR_FF_PWM_PER_RAD_S 35.0

#define MAX_PWM 240

#define HOLD_VEL_DEADBAND_LINEAR 0.05
#define HOLD_VEL_DEADBAND_ANGULAR 0.005
#define HOLD_VEL_MAX_PWM 240

#define POSITION_MAX_LINEAR_CM_S 30.0
#define POSITION_MAX_ANGULAR_RAD_S 2.0
#define POSITION_LINEAR_DEADBAND 0.0
#define POSITION_ANGULAR_DEADBAND 0.0

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
                             const PID& angular_velocity_pid,
                             const PID& linear_position_pid,
                             const PID& angular_position_pid)
    : encoder_resolution(encoder_resolution),
      center_distance(center_distance),
      wheel_diameter(wheel_diameter),
      linear_velocity_pid(linear_velocity_pid),
      angular_velocity_pid(angular_velocity_pid),
      linear_position_pid(linear_position_pid),
      angular_position_pid(angular_position_pid) {}

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
    this->linear_velocity = 0.0f;
    this->angular_velocity = 0.0f;
    this->last_linear_error = 0.0;
    this->last_angular_error = 0.0;
    this->last_linear_correction = 0.0;
    this->last_angular_correction = 0.0;
    this->last_odometrie_time = micros();
    if (this->right_motor != nullptr) {
        this->right_motor->ticks = 0L;
        this->right_motor->last_ticks = 0L;
        this->right_motor->distance = 0.0;
        this->right_motor->set_motor(0);
    }
    if (this->left_motor != nullptr) {
        this->left_motor->ticks = 0L;
        this->left_motor->last_ticks = 0L;
        this->left_motor->distance = 0.0;
        this->left_motor->set_motor(0);
    }
    this->linear_velocity_pid.reset();
    this->angular_velocity_pid.reset();
    this->linear_position_pid.reset();
    this->angular_position_pid.reset();
    this->control_mode = ControlMode::VELOCITY;
    this->target_pose = Point(x, y, theta);
    this->target_feedforward = VelocityCommand();
}

void Rolling_Basis::set_control_mode(uint8_t mode) {
    if (mode == ControlMode::POSITION) {
        this->control_mode = ControlMode::POSITION;
        this->linear_position_pid.reset();
        this->angular_position_pid.reset();
    } else {
        this->control_mode = ControlMode::VELOCITY;
        this->linear_velocity_pid.reset();
        this->angular_velocity_pid.reset();
    }
}

void Rolling_Basis::set_target_pose(const Point& pose,
                                    const VelocityCommand& feedforward) {
    this->target_pose = pose;
    this->target_feedforward = feedforward;
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
        double left_velocity = this->left_motor->filtered_velocity_cm_s;
        double right_velocity = this->right_motor->filtered_velocity_cm_s;
        this->linear_velocity = (left_velocity + right_velocity) / 2.0;
        this->angular_velocity =
            (right_velocity - left_velocity) / this->center_distance;
    }
}

/**
 * @brief Handle the correction computation
 *
 * Compute the linear and angular velocity error then apply PID and set
 * the motors new command.
 */
void Rolling_Basis::handle(const VelocityCommand& target_velocity) {
    VelocityCommand velocity_cmd = target_velocity;
    if (this->control_mode == ControlMode::POSITION) {
        double dx = this->target_pose.x - this->X;
        double dy = this->target_pose.y - this->Y;
        double cos_th = cosf(this->THETA);
        double sin_th = sinf(this->THETA);
        double linear_error = cos_th * dx + sin_th * dy;
        double angular_error =
            normalizeAngle(this->target_pose.theta - this->THETA);

        double linear_target = this->linear_position_pid.compute(linear_error);
        double angular_target =
            this->angular_position_pid.compute(angular_error);

        velocity_cmd.linear = linear_target + this->target_feedforward.linear;
        velocity_cmd.angular =
            angular_target + this->target_feedforward.angular;

        velocity_cmd.linear =
            constrain(velocity_cmd.linear, -POSITION_MAX_LINEAR_CM_S,
                      POSITION_MAX_LINEAR_CM_S);
        velocity_cmd.angular =
            constrain(velocity_cmd.angular, -POSITION_MAX_ANGULAR_RAD_S,
                      POSITION_MAX_ANGULAR_RAD_S);
    }

    bool near_zero_cmd = fabs(velocity_cmd.linear) < LINEAR_VELOCITY_ZERO_EPS &&
                         fabs(velocity_cmd.angular) < ANGULAR_VELOCITY_ZERO_EPS;

    double linear_error = velocity_cmd.linear - this->linear_velocity;
    double angular_error = velocity_cmd.angular - this->angular_velocity;

    if (near_zero_cmd && fabs(linear_error) < HOLD_VEL_DEADBAND_LINEAR &&
        fabs(angular_error) < HOLD_VEL_DEADBAND_ANGULAR) {
        this->right_motor->set_motor(0);
        this->left_motor->set_motor(0);
        this->last_linear_error = linear_error;
        this->last_angular_error = angular_error;
        this->last_linear_correction = 0.0;
        this->last_angular_correction = 0.0;
        return;
    }

    double linear_correction = this->linear_velocity_pid.compute(linear_error);
    double angular_correction =
        this->angular_velocity_pid.compute(angular_error);

    double linear_ff = LINEAR_FF_PWM_PER_CM_S * velocity_cmd.linear;
    double angular_ff = ANGULAR_FF_PWM_PER_RAD_S * velocity_cmd.angular;

    double linear_cmd = linear_correction + linear_ff;
    double angular_cmd = angular_correction + angular_ff;

    if (fabs(linear_cmd) > 0.0 && fabs(linear_cmd) < MIN_PWM_LINEAR) {
        linear_cmd = copysign(MIN_PWM_LINEAR, linear_cmd);
    }
    if (fabs(angular_cmd) > 0.0 && fabs(angular_cmd) < MIN_PWM_ANGULAR) {
        angular_cmd = copysign(MIN_PWM_ANGULAR, angular_cmd);
    }

    if (near_zero_cmd) {
        linear_cmd = constrain(linear_cmd, -HOLD_VEL_MAX_PWM, HOLD_VEL_MAX_PWM);
        angular_cmd =
            constrain(angular_cmd, -HOLD_VEL_MAX_PWM, HOLD_VEL_MAX_PWM);
    } else {
        linear_cmd = constrain(linear_cmd, -MAX_PWM, MAX_PWM);
        angular_cmd = constrain(angular_cmd, -MAX_PWM, MAX_PWM);
    }

    this->last_linear_error = linear_error;
    this->last_angular_error = angular_error;
    this->last_linear_correction = linear_cmd;
    this->last_angular_correction = angular_cmd;

    double right_pwm = linear_cmd + angular_cmd;
    double left_pwm = linear_cmd - angular_cmd;

    right_pwm = constrain(right_pwm, -MAX_PWM, MAX_PWM);
    left_pwm = constrain(left_pwm, -MAX_PWM, MAX_PWM);

    this->right_motor->set_motor(right_pwm);
    this->left_motor->set_motor(left_pwm);
}
