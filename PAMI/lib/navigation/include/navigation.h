#ifndef NAVIGATION_H
#define NAVIGATION_H

#include "motors.h"

class Navigation {
private:
    // Left motor
    Motor* _leftMotor;
    // Right motor
    Motor* _rightMotor;
    // Diameter of the wheels in mm
    float _wheelDiameterMm;
    // Distance between the two wheels in mm
    float _wheelBaseMm;

    // Check if the navigation is moving
    bool _moving;
    // Check if the navigation is a turning move
    bool _turning;

    // Initial left motor steps when navigation starts moving
    long _leftSteps;
    // Initial right motor steps when navigation starts moving
    long _rightSteps;

public:
    /**
     * Constructor
     * @param leftMotor : left motor
     * @param rightMotor : right motor
     * @param wheelDiameterMm : diameter of the wheels in mm
     * @param wheelBaseMm : distance between the two wheels in mm
     */
    Navigation(Motor* leftMotor, Motor* rightMotor, float wheelDiameterMm, float wheelBaseMm);
    // Destructor
    ~Navigation()=default;

    // Forward a given distance in mm. Negative values move the robot backward
    void forward(float distanceMm);
    // Turn a given angle in degrees. Negative values turn the robot clockwise
    void turn(float angleDeg);
    // Update the navigation
    void update();
    // Stop the navigation
    void stop();
    // Check if the navigation is moving
    bool isBusy() const { return _moving; }
};

#endif // NAVIGATION_H