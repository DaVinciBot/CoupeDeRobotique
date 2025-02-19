#ifndef MOTORS_H
#define MOTORS_H

#include <Arduino.h>

class Motor {
private:
    // Pin to control the step of the motor
    byte _stepPin;
    // Pin to control the direction of the motor
    byte _dirPin;
    // Pin to enable/disable the motor
    byte _enablePin;

    // Number of steps per revolution
    unsigned int _stepsPerRev;

    // Target speed of the motor in steps per second
    float _targetSpeed;
    // Current speed of the motor in steps per second
    float _currentSpeed;
    // Acceleration of the motor in steps per second squared
    float _acceleration;
    
    // State of the motor
    bool _moving;
    // Number of steps remaining in current move
    long _stepsRemaining;
    // Last time a step was taken
    unsigned long _lastStepTime;
    
    // Interval between steps in microseconds
    float _stepIntervalUs;

    // Direction of the motor (true = clockwise, false = counter-clockwise)
    void _setDirection(bool clockwise);
    // Take one step in the current direction
    void _doOneStep();

public:
    /**
     * Constructor
     * @param stepPin : pin de commande STEP
     * @param dirPin : pin de commande DIRECTION
     * @param enablePin : pin de commande ENABLE
     * @param stepsPerRev : nombre de pas par tour
     */
    Motor(byte stepPin, byte dirPin, byte enablePin, unsigned int stepsPerRevolution);
    // Destructor
    ~Motor()=default;

    // Initialize the motor
    void init();
    // Enable/disable the motor
    void enableMotor(bool enable);

    // Set the target speed of the motor in steps per second
    void setTargetSpeed(float stepsPerSec);
    // Set acceleration of the motor in steps per second squared
    void setAcceleration(float stepsPerSec2);
    // Prepare the motor to move a number of steps (Positive = forward, Negative = backward)
    void moveSteps(long steps);
    // Prepare the motor to move a distance in mm (Positive = forward, Negative = backward)
    void moveDistance(float distanceMm, float wheelDiameterMm);
    // Update the motor state
    void update();
    // Check if the motor is moving
    bool isMoving() const { return _moving; }
};

#endif // MOTORS_H