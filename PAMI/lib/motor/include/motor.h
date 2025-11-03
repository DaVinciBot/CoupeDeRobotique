#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>
#include <cstdint>

/**
 * @brief Class representing a stepper motor.
 *
 * This class provides a simple high-level interface to a stepper motor
 * driver using three control pins: STEP, DIR and ENABLE. It implements a
 * non-blocking update loop (`update()`) which should be called frequently
 * from the main loop or a scheduler. Speeds are represented in steps per
 * second and accelerations in steps per second squared. Microstepping is
 * supported via the `_factorK` parameter.
 *
 * Contract / behavior summary:
 * - Inputs: calls to `setTargetSpeed`, `setAcceleration`, `enableMotor`.
 *
 * - Output: pulses on `_stepPin` (STEP) and direction on `_dirPin` (DIR).
 *
 * - `update()` advances the motor state and emits steps when needed.
 *
 * - `init()` must be called once before using the motor (configures pins).
 *
 * - `enableMotor(false)` should be used to disable outputs and reduce power.
 */
class Motor {
   public:
    /**
     * @brief Construct a new Motor object
     *
     * @param stepPin Pin connected to the step control of the motor driver
     * @param dirPin Pin connected to the direction control of the motor driver
     * @param enablePin Pin connected to the enable control of the motor driver
     * @param stepsPerRevolution Number of full-steps per revolution of the
     * motor (before applying microstepping factor `k`).
     * micro-steps per full step. Typical values are 1 (full-step), 2, 4, 8, ...
     * @param invertDirection If true, the logical direction is inverted.
     *
     * @note
     * - `stepsPerRevolution` combined with `k` determines the number of
     *    micro-steps for a full revolution (used by `getStepsPerRev`).
     */
    Motor(uint8_t stepPin,
          uint8_t dirPin,
          uint8_t enablePin,
          unsigned int stepsPerRevolution,
          bool invertDirection = false);

    /**
     * @brief Destroy the Motor object
     *
     */
    ~Motor() = default;

    /**
     * @brief Initialize the motor by setting pin modes.
     *
     * Must be called once (typically in setup()).
     */
    void init();

    /**
     * @brief Enable or disable the motor outputs.
     *
     * When disabled the step and direction lines are tri-stated (depends on
     * the driver) and the motor consumes less power. This does not reset
     * internal counters.
     *
     * @param enable True to enable the motor, false to disable
     */
    void enableMotor(bool enable);

    /**
     * @brief Set the target speed for the motor (non-blocking).
     *
     * The motor will accelerate/decelerate toward this target according to
     * the currently configured acceleration value. Negative speeds indicate
     * movement in the reverse logical direction.
     *
     * @param stepsPerSec Target speed in steps per second (may be negative)
     */
    void setTargetSpeed(float stepsPerSec);

    /**
     * @brief Set the acceleration used when moving toward the target speed.
     *
     * This value controls the rate of change of the internal speed in
     * steps/sec^2. Typical values depend on the motor and mechanical load.
     *
     * @param stepsPerSec2 Target acceleration in steps per second squared
     */
    void setAcceleration(float stepsPerSec2);

    /**
     * @brief Update the motor state and perform steps when required.
     *
     * Non-blocking: call frequently (e.g., in the main loop). This method
     * updates the current speed according to acceleration, computes the
     * next step timing and toggles the step pin when a step should occur.
     */
    void update();

    /**
     * @brief Get the number of micro-steps per revolution.
     *
     * This is equal to `stepsPerRevolution * k` (where `k` is the
     * microstepping factor provided at construction).
     *
     * @return unsigned int Number of micro-steps per full revolution
     */
    unsigned int getStepsPerRev() const;

    /**
     * @brief Check if the motor is currently moving (target speed != 0).
     *
     * @return true if the motor is in motion (non-zero current or target)
     * @return false otherwise
     */
    bool isMoving() const;

    /**
     * @brief Get the cumulative step count since construction or last reset.
     *
     * Positive/negative values reflect the logical direction of movement.
     *
     * @return long current step counter
     */
    long getStepCount() const;

    /**
     * @brief Reset the internal step counter to zero.
     */
    void resetStepCount();
    void doOneSteps();

   private:
    uint8_t _stepPin;       // Pin to control the stepping of the motor
    uint8_t _dirPin;        // Pin to control the direction of the motor
    uint8_t _enablePin;     // Pin to enable/disable the motor
    //float _factorK;         // Microstepping factor (K)
    bool _invertDirection;  // Whether to invert the motor direction

    unsigned int _stepsPerRevolution;  // Full-steps per revolution divided by K
    float _targetSpeedStepsPerSec;     // Desired speed (steps/sec)
    float _currentSpeedStepsPerSec;    // Current speed (steps/sec)
    float _acceleration;               // Acceleration (steps/sec^2)

    bool _moving;                 // Whether the motor is currently moving
    unsigned long _lastStepTime;  // Last time (micros) a step was taken
    float _usDelayBetweenKSteps;  // Microsecond delay between steps
    long _stepCount;              // Total step count (signed)

    /**
     * @brief Set the logical direction output pin.
     *
     * @param clockwise True for clockwise, false for counter-clockwise
     */
    void _setDirection(bool clockwise);

    /**
     * @brief Perform K micro-steps in a single logical step operation.
     *
     * This low-level helper toggles the step pin the required number of
     * times to perform microstepping according to `_factorK`.
     */
    void _doOneSteps();
};

#endif
