#include "old_basic_actions.h"

void Basic_Movement::handle(long current_right_ticks, long current_left_ticks, Motor *right_motor, Motor *left_motor){
    this->step_action->handle(current_right_ticks, current_left_ticks, right_motor, left_motor);
    this->state = this->step_action->state;
}

bool Basic_Movement::is_finished(){
    return this->state == finished;
}

Move_Straight::Move_Straight(float target_x, float target_y, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision)
{
    this->target_x = target_x;
    this->target_y = target_y;
    this->speed = speed;
    this->dir = dir;
    this->params.end_movement_presicion = end_movement_presicion;
    this->params.error_precision = error_precision;
    this->params.trajectory_precision = trajectory_precision;
}
void Move_Straight::compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params)
{
    float distance = Point.distance
     float delta_x = fabs(fabs(target_x) - fabs(current_x));
    float delta_y = fabs(fabs(target_y) - fabs(current_y));

    float distance = sqrt((delta_x * delta_x) + (delta_y * delta_y)) * this->dir;
    this->step_action = new Step_Forward_Backward(distance, this->speed, this->params);
    this->step_action->compute(
        current_right_ticks, 
        current_left_ticks, 
        rolling_basis_params->encoder_resolution, 
        rolling_basis_params->wheel_perimeter, 
        rolling_basis_params->radius
    );
    this->is_computed = true;
}

Get_Orientation::Get_Orientation(float target_x, float target_y, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision)
{
    this->target_x = target_x;
    this->target_y = target_y;
    this->speed = speed;
    this->dir = dir;
    this->params.end_movement_presicion = end_movement_presicion;
    this->params.error_precision = error_precision;
    this->params.trajectory_precision = trajectory_precision;
}
void Get_Orientation::compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params)
{
    float delta_x = this->target_x - current_x;
    float delta_y = this->target_y - current_y;
    float theta;

    // Extremum rotation
    // delta y null
    if (delta_y == 0)
    {
        if (target_x > current_x)
            theta = 0.0;
        else if (target_x < current_x)
            theta = PI;
    }
    // delta x null
    else if (delta_x == 0)
    {
        if (target_y > current_y)
            theta = PI / 2.0;
        else if (target_x < current_y)
            theta = -(PI / 2.0);
    }

    // Any cases
    else
        theta = fmod((atan2(delta_y, delta_x) - current_theta + PI), (2 * PI)) - PI;

    if (this->dir == backward)
        theta += PI;

    this->step_action = new Step_Rotation(theta, this->speed, this->params);
    this->step_action->compute(
        current_right_ticks,
        current_left_ticks,
        rolling_basis_params->encoder_resolution,
        rolling_basis_params->wheel_perimeter,
        rolling_basis_params->radius
    );
    this->is_computed = true;
}

Move_Rotation::Move_Rotation(float target_theta, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision){
    this->target_theta = target_theta;
    this->speed = speed;
    this->dir = dir;
    this->params.end_movement_presicion = end_movement_presicion;
    this->params.error_precision = error_precision;
    this->params.trajectory_precision = trajectory_precision;
}
void Move_Rotation::compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params)
{
    float mod_current_theta = fmod(current_theta, 2.0 * PI);
    if (this->dir == backward)
        mod_current_theta += PI;

    float delta_theta = this->target_theta - mod_current_theta;
    this->step_action = new Step_Rotation(delta_theta, this->speed, this->params);
    this->step_action->compute(
        current_right_ticks, current_left_ticks,
        rolling_basis_params->encoder_resolution,
        rolling_basis_params->wheel_perimeter,
        rolling_basis_params->radius
    );
    this->is_computed = true;
}
