/**
 * This is the Rolling Basis class header.
 * The Rolling Basis class is the core of the Motor teensy code.
 * It provides method to control the motors, the speed and the orientation.
 * It computes the odometry and correct the motors error with the PID class.
 */

#include <Arduino.h>
#include <motors_driver.h>
#include <pid.h>
#include "structures.h"

#include <com.h>  // Communication object to manage the communication between the teensy and the Raspberry Pi

class Rolling_Basis {
   public:
    // PID controllers
    PID linear_distance_pid;
    PID angular_distance_pid;

    // Rolling basis's params
    inline double radius() { return this->center_distance / 2.0; };
    inline double wheel_perimeter() { return this->wheel_diameter * PI; };
    inline double wheel_unit_tick_cm() {
        return this->wheel_perimeter() / this->encoder_resolution;
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

    // Rolling basis params
    unsigned short encoder_resolution;
    double center_distance;
    double wheel_diameter;

    // Constructor
    /**
     * @brief constructor of the Rolling Basis class
     *
     * Initializes the parameters of the Rolling Basis
     */
    Rolling_Basis(unsigned short encoder_resolution,
                  double center_distance,
                  double wheel_diameter,
                  const PID& linear_distance_pid,
                  const PID& angular_distance_pid);

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
     * Compute the distance and orientation error in terms of position.A0
     * Compute the PID and set the motors new command.
     */
    void handle(Point target_position, Com* com);

    void pi_mod_signed(double theta);

    // Motors action function
    // void keep_position(long current_right_ticks, long current_left_ticks);
    // void shutdown_motor();
};
