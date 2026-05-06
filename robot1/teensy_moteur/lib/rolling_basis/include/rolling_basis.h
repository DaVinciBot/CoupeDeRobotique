/**
 * This is the Rolling Basis class header.
 * The Rolling Basis class is the core of the Motor teensy code.
 * It provides methods to control the motors from pose errors.
 * It computes the odometry and correct the motors error with the PID class.
 */

#include <Arduino.h>
#include <motors_driver.h>
#include <pid.h>
#include "structures.h"

#include <com.h>  // Communication object to manage the communication between the teensy and the Raspberry Pi

class Rolling_Basis {
   public:
    // Constructor
    /**
     * @brief constructor of the Rolling Basis class
     *
     * Initializes the parameters of the Rolling Basis
     */
    Rolling_Basis(unsigned short encoder_resolution,
                  double center_distance,
                  double left_wheel_diameter,
                  double right_wheel_diameter,
                  const PID& linear_position_pid,
                  const PID& angular_position_pid,
                  const PID& left_wheel_position_pid,
                  const PID& right_wheel_position_pid);

    // Rolling basis params
    unsigned short encoder_resolution;
    double center_distance;
    double left_wheel_diameter;
    double right_wheel_diameter;

    // PID controllers
    PID linear_position_pid;
    PID angular_position_pid;
    PID left_wheel_position_pid;
    PID right_wheel_position_pid;
    Point target_position;

    // Rolling basis's params
    inline double radius() { return this->center_distance / 2.0; };
    inline double left_wheel_perimeter() {
        return this->left_wheel_diameter * PI;
    };
    inline double right_wheel_perimeter() {
        return this->right_wheel_diameter * PI;
    };
    inline double left_wheel_unit_tick_cm() {
        return this->left_wheel_perimeter() / this->encoder_resolution;
    };
    inline double right_wheel_unit_tick_cm() {
        return this->right_wheel_perimeter() / this->encoder_resolution;
    };

    // Properties
    /**
     * @brief Get current position (X, Y and THETA) of the robot
     *
     * @return Current position
     */
    Point get_current_position();

    // Rolling basis's motors
    Motor* right_motor;
    Motor* left_motor;

    // Odometrie
    double X = 0.0f;
    double Y = 0.0f;
    double THETA = 0.0f;
    unsigned long last_odometrie_time = 0;

    volatile double last_linear_error = 0.0;
    volatile double last_angular_error = 0.0;
    volatile double last_linear_correction = 0.0;
    volatile double last_angular_correction = 0.0;
    volatile double last_left_wheel_error = 0.0;
    volatile double last_right_wheel_error = 0.0;
    volatile double left_wheel_target_cm = 0.0;
    volatile double right_wheel_target_cm = 0.0;
    volatile bool manual_pwm_active = false;
    volatile int16_t manual_left_pwm = 0;
    volatile int16_t manual_right_pwm = 0;
    volatile uint32_t manual_pwm_until_ms = 0;

    /**
     * @brief Destructor of Rolling Basis class
     */
    ~Rolling_Basis() = default;

    // Inits function
    /**
     * @brief Define right motor with pins, related encoders pin and properties
     * of the wheel attached to the motor.
     */
    void define_right_motor(byte enca,
                            byte encb,
                            byte pwm,
                            byte in2,
                            byte in1,
                            byte max_pwm);
    /**
     * @brief Define left motor with pins, related encoders pin and properties
     * of the wheel attached to the motor.
     */
    void define_left_motor(byte enca,
                           byte encb,
                           byte pwm,
                           byte in2,
                           byte in1,
                           byte max_pwm);
    /**
     * @brief Initialize both motors
     */
    void init_motors();
    /**
     * @brief Initialize Rolling Basis state with starting position
     */
    void init_rolling_basis(double x, double y, double theta);

    // Odometrie function
    /**
     * @brief Handle the odometry computation
     *
     * Update motors position sthen compute displacement of both motors.
     * The with these results, estimate the robot position and orientation.
     * Finally update the rolling basis state.
     */
    void odometrie_handle();
    /**
     * @brief Handle the correction computation
     *
     * Compute the distance and orientation error, then directly command PWM.
     */
    void handle();

    void set_target_position(const Point& position);
    void set_motors_pwm(int16_t left_pwm,
                        int16_t right_pwm,
                        uint32_t duration_ms);

    void pi_mod_signed(double theta);

    // Motors action function
    // void keep_position(long current_right_ticks, long current_left_ticks);
    // void shutdown_motor();
};
