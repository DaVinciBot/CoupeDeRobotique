#include "old_complex_actions.h"

bool Complex_Action::is_finished()
{
    return this->state == finished;
}
void Complex_Action::alloc_memory(short nb_actions){
    this->basic_actions_list_size = nb_actions;
    this->basic_actions = new Basic_Movement*[nb_actions];
}

void Complex_Action::handle(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Motor *right_motor, Motor *left_motor, Rolling_Basis_Params *rolling_basis_params)
{
    if(!this->is_computed)
        this->compute(current_x, current_y, current_theta, current_right_ticks, current_left_ticks, rolling_basis_params);
    if (0 <= this->action_index && this->action_index < this->basic_actions_list_size){
        this->state = in_progress;

        // Compute the next action
        if (!this->basic_actions[this->action_index]->is_computed){
            this->basic_actions[this->action_index]->compute(
                current_x, current_y, current_theta,
                current_right_ticks, current_left_ticks,
                rolling_basis_params
            );
        }       
        // Handle action
        else if (
            this->basic_actions[this->action_index]->is_computed && 
            (this->basic_actions[this->action_index]->state == not_started || this->basic_actions[this->action_index]->state == in_progress)
        )
        {
            this->basic_actions[this->action_index]->handle(current_right_ticks, current_left_ticks, right_motor, left_motor);
        }
        // End of the action
        else if (this->basic_actions[this->action_index]->is_finished())
        {
            this->action_index++;
        }
    }
    else {
        this->state = finished;
    }
}

// Go to
Go_To::Go_To(float target_x, float target_y, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision)
{
    this->target_x = target_x;
    this->target_y = target_y;
    this->dir = dir;
    this->speed = speed;
    this->params.end_movement_presicion = end_movement_presicion;
    this->params.error_precision = error_precision;
    this->params.trajectory_precision = trajectory_precision;
}



/*
// Curve go to
Curve_Go_To::Curve_Go_To(float target_x, float target_y, float circle_center_x, float circle_center_y, int ticks_interval, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision)
{
    this->target_x = target_x;
    this->target_y = target_y;
    this->circle_center_x = circle_center_x;
    this->circle_center_y = circle_center_y;
    this->ticks_interval = ticks_interval;
    this->dir = dir;
    this->speed = speed;
    this->params.end_movement_presicion = end_movement_presicion;
    this->params.error_precision = error_precision;
    this->params.trajectory_precision = trajectory_precision;
}

void Curve_Go_To::compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params){
    // Calcul cercle radius
    float delta_x = this->target_x - this->circle_center_x;
    float delta_y = this->target_y - this->circle_center_y;
    float radius = sqrt(delta_x * delta_x + delta_y * delta_y);

    float target_angle = atan2(this->target_y - this->circle_center_y, this->target_x - this->circle_center_x);
    float current_angle = atan2(current_y - this->circle_center_y, current_x - this->circle_center_x);

    float dif_angle = target_angle - current_angle;
    float distance = radius * dif_angle;

    // Calcul nb of points on the trajectory
    int nb_points = distance / this->ticks_interval;
    this->alloc_memory(nb_points * 2);

    for (int k = 0; k < nb_points; k++) {
        // Calcul the coordonates of the point
        float x = this->circle_center_x + radius * cos(current_angle + k * dif_angle / nb_points);
        float y = this->circle_center_y + radius * sin(current_angle + k * dif_angle / nb_points);

        this->basic_actions[k] = new Get_Orientation(
            x, y,
            this->dir,
            this->speed,
            this->params.end_movement_presicion,
            this->params.error_precision,
            this->params.trajectory_precision);
        this->basic_actions[k+1] = new Move_Straight(
            x, y,
            this->dir,
            this->speed,
            this->params.end_movement_presicion,
            this->params.error_precision,
            this->params.trajectory_precision);
    }
    this->is_computed = true;
} */