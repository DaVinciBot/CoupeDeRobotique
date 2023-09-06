#include "old_step_actions.h"

bool Step_Movement::is_finished(){
    return this->state == finished;
}

void Step_Movement::check_end_of_action(long current_right_ticks, long current_left_ticks)
{
    long right_error = abs(this->right_ref + this->right_sign * this->total_ticks) - abs(current_right_ticks);
    long left_error = abs(this->left_ref + this->left_sign * this->total_ticks) - abs(current_left_ticks);

    // Check if the robot is near the target position
    if ((long)this->params.error_precision >= right_error && (long)this->params.error_precision >= left_error)
        (this->end_movement_cpt)++;

    // Checks if the robot has been in the right position long enough end the action
    if (this->end_movement_cpt >= this->params.end_movement_presicion)
        this->state = finished;
    else
        this->state = in_progress;
}

void Step_Movement::update_action_cursor(long current_right_ticks, long current_left_ticks){

    long right_error = this->ticks_cursor - abs(current_right_ticks - this->right_ref);
    long left_error = this->ticks_cursor - abs(current_left_ticks - this->left_ref);

    // Do we need to correct the trajectory ?
    if (abs(right_error) <= this->params.trajectory_precision && abs(left_error) <= this->params.trajectory_precision)
    {
        if (abs(this->ticks_cursor - this->total_ticks) < this->params.error_precision)
            this->ticks_cursor = this->total_ticks;
        else
            this->ticks_cursor += this->params.trajectory_precision;

        if (this->ticks_cursor > this->total_ticks)
            this->ticks_cursor = this->total_ticks;
    }
}

void Step_Movement::handle(long current_right_ticks, long current_left_ticks, Motor *right_motor, Motor *left_motor)
{
    this->check_end_of_action(current_right_ticks, current_left_ticks);
    this->update_action_cursor(current_right_ticks, current_left_ticks);

    // Set motor order
    right_motor->handle((this->right_ref + this->right_sign * this->ticks_cursor), this->speed);
    left_motor->handle((this->left_ref + this->left_sign * this->ticks_cursor), this->speed);
}

// Move Forward or Backward
Step_Forward_Backward::Step_Forward_Backward(float distance, byte speed, Movement_Params params)
{
    this->distance = fabs(distance);
    this->speed = speed;
    this->dir = (distance < 0) ? backward : forward;
    this->params = params;
}

void Step_Forward_Backward::compute(long current_right_ticks, long current_left_ticks, int encoder_resolution, float wheel_perimeter, float radius)
{
    this->total_ticks = (encoder_resolution / wheel_perimeter) * this->distance;
    if (this->dir == forward)
    {
        this->right_sign = 1;
        this->left_sign = 1;
    }
    else if (this->dir == backward)
    {
        this->right_sign = -1;
        this->left_sign = -1;
    }

    this->right_ref = current_right_ticks;
    this->left_ref = current_left_ticks;
    this->is_computed = true;
}

// Move Rotation
Step_Rotation::Step_Rotation(float theta, byte speed, Movement_Params params)
{
    this->theta = fabs(theta);
    this->speed = speed;
    this->rotation_dir = (theta < 0) ? clockwise : counterclockwise;
    this->params = params;
}

void Step_Rotation::compute(long current_right_ticks, long current_left_ticks, int encoder_resolution, float wheel_perimeter, float radius)
{
    float distance = (fabs(this->theta) * radius);
    this->total_ticks = (encoder_resolution / wheel_perimeter) * distance;

    if (this->rotation_dir == counterclockwise)
    {
        this->right_sign = 1;
        this->left_sign = -1;
    }
    else if (this->rotation_dir == clockwise)
    {
        this->right_sign = -1;
        this->left_sign = 1;
    }

    this->right_ref = current_right_ticks;
    this->left_ref = current_left_ticks;
    this->is_computed = true;
}
