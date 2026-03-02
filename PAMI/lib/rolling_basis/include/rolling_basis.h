#ifndef ROLLING_BASIS_H
#define ROLLING_BASIS_H

#include "motor.h"
#include "pid.h"
#include "point.h"

/**
 * @brief Class representing the rolling basis for the robot.
 *
 * This class wraps two `Motor` objects to provide differential-drive
 * behavior (also called a rolling basis). It accepts high-level position
 * targets (x, y, theta in `Point`) and executes a two-phase motion:
 * rotate toward the target heading, then drive forward to reach the
 * target position. All linear distances are in millimeters and angles in
 * radians.
 *
 * Design notes / contract:
 *
 * - Coordinates and pose: `Point` is expected to be {x(mm), y(mm), theta(rad)}.
 *
 * - setCommand schedules a motion to the specified pose. If called while
 *   moving, the command replaces the current target.
 *
 * - update() must be called periodically (e.g., in the main loop) to
 *   progress the state machine. It performs time-based control and sends
 *   wheel speed commands to the motors.
 *
 * - stop() immediately stops both motors and sets phase to Idle.
 */
class RollingBasis {
   public:
    /**
     * @brief Enumeration representing the different phases of motion.
     *
     * @note
     * - Idle: no motion
     *
     * - Rotating: robot rotates in place to align heading with target
     *
     * - Forwarding: robot drives straight toward the target position
     *
     * - Done: motion finished (arrived at target)
     */
    enum class Phase { Idle, Rotating, Forwarding, Done };

    /**
     * @brief Construct a new Rolling Basis object
     *
     * @param leftMotor Pointer to the left `Motor` instance (must not be null)
     * @param rightMotor Pointer to the right `Motor` instance (must not be
     * null)
     * @param wheelDiameterMm Diameter of the wheels in millimeters
     * @param wheelBaseMm Distance between the wheels (track width) in
     * millimeters
     * @param initialPosition Initial pose of the robot (x(mm), y(mm),
     * theta(rad))
     *
     * @note
     * - The motors provided are already initialized via `Motor::init()`.
     */
    RollingBasis(Motor* leftMotor,
                 Motor* rightMotor,
                 float wheelDiameterMm,
                 float wheelBaseMm,
                 const Point& initialPosition = {0, 0, 0});

    /**
     * @brief Destroy the Rolling Basis object
     */
    ~RollingBasis() = default;

    /**
     * @brief Set a new motion command (target pose).
     *
     * The command defines the desired absolute pose. The rolling basis will
     * first rotate to align with the goal heading, then drive forward.
     *
     * @param target Target position and orientation (Point: x(mm), y(mm),
     * theta(rad))
     */
    void setCommand(const Point& target);

    /**
     * @brief Update the state machine and control outputs.
     *
     * Call frequently. The method computes elapsed time since the last
     * call, updates odometry (if wheel encoders are used), advances the
     * phase state machine and sends wheel speeds to the motors via
     * `_sendWheelSpeeds`.
     */
    void update();

    /**
     * @brief Returns true if the rolling basis is currently executing a
     * command.
     *
     * @return true if phase is Rotating or Forwarding
     * @return false if Idle or Done
     */
    bool isMoving() const;

    /**
     * @brief Stop the rolling basis immediately and disable motion.
     *
     * This will command zero wheel speeds and set the internal phase to
     * Idle. It does not change the internal odometry pose.
     */
    void stop();

    /**
     * @brief Get the current estimated pose of the robot.
     *
     * @return Point pose as {x(mm), y(mm), theta(rad)}
     */
    Point getPose() const;

    /**
     * @brief Get the current linear speed estimate in mm/s.
     *
     * @return float linear speed in millimeters per second
     */
    float getLinearSpeedMmPerS() const;

    /**
     * @brief Get the current angular speed estimate in rad/s.
     *
     * @return float angular speed in radians per second
     */
    float getAngularSpeedRadPerS() const;
    /**
     * @brief defined the speed for the two motors
     *
     * @return an avancement (?)
     */
    void setSpeed(float linearMmPerS, float angularRadPerS);
    /**
     * @brief update the motors
     *
     * @return do the update
     */
    void updateMotors();

   private:
    // void _computeOdometry(float dt);
    // void _applyControl(float dt);

    /**
     * @brief Normalize an angle to the range [-pi, pi].
     *
     * @param ang Angle in radians
     * @return float Normalized angle in radians
     */
    float _wrapToPi(float ang) const;

    /**
     * @brief Convert linear/angular velocity commands to individual wheel
     * speeds and send them to the motors.
     *
     * @param v Linear speed in mm/s
     * @param w Angular speed in rad/s
     *
     * @note The method computes left/right wheel speeds using
     * differential-drive kinematics (v_left = v - w*base/2, v_right = v +
     * w*base/2) and maps linear wheel speeds to motor step rates using wheel
     * circumference.
     */
    void _sendWheelSpeeds(float v, float w);

    Motor* _leftMotor;       // Pointer to the left motor
    Motor* _rightMotor;      // Pointer to the right motor
    float _wheelDiameterMm;  // Wheel diameter in millimeters
    float _wheelBaseMm;  // Distance between wheels (track width) in millimeters

    // long _prevLeftSteps;   // Previous left motor steps
    // long _prevRightSteps;  // Previous right motor steps

    Point _currentPose;   // Current estimated pose {x(mm),y(mm),theta(rad)}
    float _linearSpeed;   // Current linear speed estimate in mm/s
    float _angularSpeed;  // Current angular speed estimate in rad/s
    Phase _phase;         // Current motion phase

    float _rotateDuration;   // Planned rotation duration (s)
    float _forwardDuration;  // Planned forwarding duration (s)
    /**
     * @brief Rotation direction: +1 for clockwise, -1 for counter-clockwise.
     *
     * Stored as float for convenience when multiplying with durations/speeds.
     */
    float _rotateDirection;
    // Start time of the current phase
    unsigned long _startTime;
};

#endif
