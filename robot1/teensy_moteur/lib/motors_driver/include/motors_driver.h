/**
 * This is the Motor class header.
 * The Motor class control a Mmotor power and direction and handle odometry
 * computation.
 */

#include <Arduino.h>

// Motor class
class Motor {
   private:
    // Pins Motor
    byte pin_forward;
    byte pin_backward;
    byte pin_pwm;   // PWM pin only !
    byte pin_enca;  // AttachInterrupt pin only !
    byte pin_encb;  // AttachInterrupt pin only !

    byte max_pwm;
    byte min_moving_pwm;
    byte pwm_slew_per_cycle;
    int16_t current_pwm = 0;

    // Ticks distance
    double wheel_unit_tick_cm;

   public:
    volatile long ticks = 0L;
    volatile int16_t last_pwm = 0;

    // Motor description (it is the last data calculated by the motor odometer
    // handle method)
    double distance = 0.0;  // Distance in cm
    long last_ticks = 0L;   // Ticks distance used to compute distance
                            // (updated at the last odometer handle call)
    long last_delta_ticks = 0L;
    // Constructor
    /**
     * @brief Constructor of the Motor class
     * Define the pins of the motor, the related encoder pins and the properties
     * of the wheel attached to the motor
     */
    Motor(byte pin_forward,
          byte pin_backward,
          byte pin_pwm,
          byte pin_enca,
          byte pin_encb,
          double wheel_unit_tick_cm,
          byte max_pwm,
          byte min_moving_pwm,
          byte pwm_slew_per_cycle);
    ~Motor() = default;

    // Methods
    /**
     * @brief Initialize the mode of the pins define for the motor
     */
    void init();

    /**
     * @brief Set motor PWM and direction
     *
     * @param pwmVal Power value of the motor
     */
    void set_motor(int pwmVal);
    void set_motor_raw(int pwmVal);

    void handle_odometrie();
};
