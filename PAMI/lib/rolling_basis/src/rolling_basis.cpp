#include "rolling_basis.h"
#include <math.h>

RollingBasis::RollingBasis(Motor *leftMotor, Motor *rightMotor,
                           float wheelDiameterMm, float wheelBaseMm)
    : _leftMotor(leftMotor), _rightMotor(rightMotor),
      _wheelDiameterMm(wheelDiameterMm), _wheelBaseMm(wheelBaseMm),
      _previousLeftStepCount(0), _lastRightStepCount(0),
      _x(0), _y(0), _theta(0)
{
    _leftMotor->resetStepCount();
    _rightMotor->resetStepCount();
}

void RollingBasis::setLinearAngularSpeed(float linearMmS, float angularDegS)
{
    float angularRadS = angularDegS * (M_PI / 180.0f);
    float halfBase = _wheelBaseMm / 2.0f;
    float leftVel = linearMmS - angularRadS * halfBase;
    float rightVel = linearMmS + angularRadS * halfBase;
    float circumference = M_PI * _wheelDiameterMm;

    float leftStepsPerSec = (leftVel / circumference) * _leftMotor->getStepsPerRev();
    float rightStepsPerSec = (rightVel / circumference) * _rightMotor->getStepsPerRev();

    _leftMotor->setTargetSpeed(leftStepsPerSec);
    _rightMotor->setTargetSpeed(rightStepsPerSec);
}

void RollingBasis::update()
{
    _leftMotor->update();
    _rightMotor->update();

    long leftSteps = _leftMotor->getStepCount();
    long rightSteps = _rightMotor->getStepCount();

    long dL = leftSteps - _previousLeftStepCount;
    long dR = rightSteps - _lastRightStepCount;
    _previousLeftStepCount = leftSteps;
    _lastRightStepCount = rightSteps;

    float mmPerStep = (M_PI * _wheelDiameterMm) / _leftMotor->getStepsPerRev();
    float dLeft = dL * mmPerStep;
    float dRight = dR * mmPerStep;

    float dCenter = (dLeft + dRight) / 2.0f;
    float dTheta = (dRight - dLeft) / _wheelBaseMm;

    float dx = dCenter * cos(_theta + dTheta / 2.0f);
    float dy = dCenter * sin(_theta + dTheta / 2.0f);
    _x += dx;
    _y += dy;
    _theta += dTheta;
}

bool RollingBasis::isMoving() const
{
    return _leftMotor->isMoving() || _rightMotor->isMoving();
}

void RollingBasis::stop()
{
    _leftMotor->setTargetSpeed(0);
    _rightMotor->setTargetSpeed(0);
}

void RollingBasis::getPose(float &x, float &y, float &theta) const
{
    x = _x;
    y = _y;
    theta = _theta;
}

void RollingBasis::resetPose()
{
    _x = _y = _theta = 0;
    _leftMotor->resetStepCount();
    _rightMotor->resetStepCount();
    _previousLeftStepCount = _lastRightStepCount = 0;
}

// TODO: checker travail flo :

/*
Odometrie function
void Rolling_Basis::odometrie_handle(){
    // Save last motors positions
double last_right_distance = this->right_motor->distance;
double last_left_distance = this->left_motor->distance;

// Update motors positions by calling odometer_handle
ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
{
    this->right_motor->odometer_handle();
    this->left_motor->odometer_handle();
}

// Compute motors deplacement
double right_move = this->right_motor->distance - last_right_distance;
double left_move = this->left_motor->distance - last_left_distance;

// Determine the position of the robot
float movement_difference = right_move - left_move;
float movement_sum = (right_move + left_move) / 2;

this->THETA = this->THETA - (movement_difference / this->center_distance);
this->X = this->X + (cos(this->THETA) * movement_sum);
this->Y = this->Y + (sin(this->THETA) * movement_sum);
}

void Rolling_Basis::handle(
    Point target_position,
    float target_linear_speed, float target_angular_speed)
{
    // Speed part
    // Compute real linear and angular speed
    double Vm = (this->right_motor->speed + this->left_motor->speed) / 2;                     // Vitesse linéaire mesurée
    double Wm = (this->right_motor->speed - this->left_motor->speed) / this->center_distance; // Vitesse angulaire mesurée

    // Save speeds as rolling basis properties
    this->linear_speed = (float)Vm;
    this->angular_speed = (float)Wm;

    // Compute linear and angular speed error (difference between target and real)
    double Ev = target_linear_speed - Vm;
    double Ew = target_angular_speed - Wm;

    // Compute PID output based on errors
    double linear_speed_correction = this->linear_speed_pid.compute(Ev);
    double angular_speed_correction = this->angular_speed_pid.compute(Ew);

    // Position part
    // We already have the current robot's position with odometrie (X, Y, THETA)

    // Compute distance and orientation error (difference between target and real)
    double Ed = sqrt(pow(target_position.x - this->X, 2) + pow(target_position.y - this->Y, 2));
    double Etheta = target_position.theta - fmod(this->THETA, PI); // fmod to keep the angle between -PI and PI, TODO: a tester !!

    // Compute PID output based on errors
    double linear_distance_correction = this->linear_distance_pid.compute(Ed);
    double angular_distance_correction = this->angular_distance_pid.compute(Etheta);

    // Combine both corrections
    // Compute corrected linear and angular speed
    double Vc = target_linear_speed + linear_speed_correction + linear_distance_correction;
    double Wc = target_angular_speed + angular_speed_correction + angular_distance_correction;

    // Compute right and left motor speed
    double right_speed = (2 * Vc + Wc * this->center_distance) / 2;
    double left_speed = (2 * Vc - Wc * this->center_distance) / 2;

    // Apply commands to motors
    this->right_motor->set_motor(right_speed);
    this->left_motor->set_motor(left_speed);
}
*/