#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>
#include <cstdint>

/**
 * @brief Class representing a stepper motor.
 *
 */
class Motor {
    /**
     * @brief Construct a new Motor object
     *
     * @param stepPin Pin connected to the step control of the motor driver
     * @param dirPin Pin connected to the direction control of the motor driver
     * @param enablePin Pin connected to the enable control of the motor driver
     * @param stepsPerRevolution Number of steps per revolution of the motor
     * @param k Factor K for microstepping
     * @param invertDirection Whether to invert the direction of the motor
     *
     */
    Motor(uint8_t stepPin,
          uint8_t dirPin,
          uint8_t enablePin,
          unsigned int stepsPerRevolution,
          float k,
          bool invertDirection = false);
    /**
     * @brief Destroy the Motor object
     *
     */
    ~Motor() = default;

    /**
     * @brief Initialize the motor by setting pin modes
     *
     */
    void init();
    /**
     * @brief Enable or disable the motor
     *
     * @param enable True to enable the motor, false to disable
     *
     */
    void enableMotor(bool enable);

    /**
     * @brief Set the Target Speed of the motor
     *
     * @param stepsPerSec Target speed in steps per second
     *
     */
    void setTargetSpeed(float stepsPerSec);
    /**
     * @brief Set the Acceleration of the motor
     *
     * @param stepsPerSec2 Target acceleration in steps per second squared
     *
     */
    void setAcceleration(float stepsPerSec2);
    /**
     * @brief Update the motor state.
     *
     * Should be called periodically.
     *
     */
    void update();

    /**
     * @brief Get the number of Steps done per Revolution
     *
     * @return unsigned int
     */
    unsigned int getStepsPerRev() const;
    /**
     * @brief Check if the motor is currently moving
     *
     * @return true
     * @return false
     */
    bool isMoving() const;

    /**
     * @brief Get the current Step Count
     *
     * @return long
     */
    long getStepCount() const;
    /**
     * @brief Reset the Step Count to zero
     *
     */
    void resetStepCount();

   private:
    uint8_t _stepPin;       // Pin to control the stepping of the motor
    uint8_t _dirPin;        // Pin to control the direction of the motor
    uint8_t _enablePin;     // Pin to enable/disable the motor
    float _factorK;         // Microstepping factor K
    bool _invertDirection;  // Whether to invert the motor direction

    unsigned int _stepsPerRevolution;  // Steps per revolution divided by K
    float _targetSpeedStepsPerSec;     // Target speed in steps per second
    float _currentSpeedStepsPerSec;    // Current speed in steps per second
    float _acceleration;  // Acceleration in steps per second squared

    bool _moving;                 // Whether the motor is currently moving
    unsigned long _lastStepTime;  // Last time a step was taken
    float _usDelayBetweenKSteps;  // Microseconds delay between K steps
    long _stepCount;              // Total step count

    /**
     * @brief Set the direction of the motor
     *
     * @param clockwise True for clockwise, false for counter-clockwise
     *
     */
    void _setDirection(bool clockwise);
    // Perform K steps
    void _doKSteps();
};

#endif
