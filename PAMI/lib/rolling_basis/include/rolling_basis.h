#ifndef ROLLING_BASIS_H
#define ROLLING_BASIS_H

#include <chrono>
#include "motor.h"
#include "pid.h"
#include "point.h"

/**
 * @brief Class representing the rolling basis for the robot.
 *
 */
class RollingBasis {
   public:
    /**
     * @brief Enumeration representing the different phases of the rolling
     * basis.
     *
     */
    enum class Phase { Idle, Rotating, Forwarding, Done };
    /**
     * @brief Construct a new Rolling Basis object
     *
     * @param leftMotor Pointer to the left motor
     * @param rightMotor Pointer to the right motor
     * @param wheelDiameterMm Diameter of the wheels in millimeters
     * @param wheelBaseMm Distance between the wheels in millimeters
     * @param initialPosition Initial position of the robot
     *
     */
    RollingBasis(Motor* leftMotor,
                 Motor* rightMotor,
                 float wheelDiameterMm,
                 float wheelBaseMm,
                 const Point& initialPosition = {0, 0, 0});
    /**
     * @brief Destroy the Rolling Basis object
     *
     */
    ~RollingBasis() = default;

    /**
     * @brief Set the command for the rolling basis
     *
     * @param target Target position and orientation
     *
     */
    void setCommand(const Point& target);

    /**
     * @brief Update the state of the rolling basis
     *
     * Should be called periodically.
     *
     */
    void update();

    /**
     * @brief Check if the rolling basis is currently moving
     *
     * @return true
     * @return false
     */
    bool isMoving() const;
    /**
     * @brief Stop the rolling basis immediately
     *
     */
    void stop();

    /**
     * @brief Get the current position and orientation of the robot
     *
     * @return Point
     */
    Point getPose() const;
    /**
     * @brief Get the Linear Speed of the robot in mm/s
     *
     * @return float
     */
    float getLinearSpeedMmPerS() const;
    /**
     * @brief Get the Angular Speed of the robot in rad/s
     *
     * @return float
     */
    float getAngularSpeedRadPerS() const;

   private:
    // void _computeOdometry(float dt);
    // void _applyControl(float dt);
    /**
     * @brief Wrap angle to the range [-pi, pi]
     *
     * @param ang Angle in radians
     * @return float
     */
    float _wrapToPi(float ang) const;
    /**
     * @brief Send wheel speeds to the motors
     *
     * @param v Linear speed in mm/s
     * @param w Angular speed in rad/s
     *
     */
    void _sendWheelSpeeds(float v, float w);

    Motor* _leftMotor;       // Pointer to the left motor
    Motor* _rightMotor;      // Pointer to the right motor
    float _wheelDiameterMm;  // Diameter of the wheels in millimeters
    float _wheelBaseMm;      // Distance between the wheels in millimeters

    // long _prevLeftSteps;   // Previous left motor steps
    // long _prevRightSteps;  // Previous right motor steps

    Point _currentPose;   // Current position and orientation of the robot
    float _linearSpeed;   // Linear speed of the robot in mm/s
    float _angularSpeed;  // Angular speed of the robot in rad/s
    Phase _phase;         // Current phase of the rolling basis

    float _rotateDuration;   // Duration of the rotation phase
    float _forwardDuration;  // Duration of the forwarding phase
    // Direction of the rotation (1 for clockwise, -1 for counter-clockwise)
    float _rotateDirection;
    std::chrono::steady_clock::time_point
        _startTime;  // Start time of the current phase

    // PID _linDistPid;  // PID controller for linear distance
    // PID _angDistPid;  // PID controller for angular distance

    // float _cmdLinSpeed;  // Commanded linear speed in mm/s
    // float _cmdAngSpeed;  // Commanded angular speed in rad/s
    // Point _cmdPosition;  // Target position and orientation

    // float _measLinSpeed;  // Measured linear speed in mm/s
    // float _measAngSpeed;  // Measured angular speed in rad/s

    // std::chrono::steady_clock::time_point _lastTime;  // Last update time
    // bool _moving;  // Whether the rolling basis is currently moving
};

#endif
