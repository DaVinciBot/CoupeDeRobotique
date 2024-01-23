#include <basic_action.h>

// Basic deplacement action generic class
void Basic_Action::handle(Point current_point, Ticks current_ticks, Rolling_Basis_Ptrs *rolling_basis_ptrs)
{
    // Check if the action is computed
    if (!this->is_computed)
        this->compute(current_point, current_ticks, rolling_basis_ptrs->rolling_basis_params);

    // Handle the action
    else if (this->state == not_started || this->state == in_progress)
        this->step_action->handle(current_point, current_ticks, rolling_basis_ptrs);

    // Update action state base on the step action state
    this->state = this->step_action->state;
}

// Move Straight
Move_Straight::Move_Straight(float target_x, float target_y, Direction *direction, Speed_Driver *speed_driver, Precision_Params *precision_params)
{
    this->target_x = target_x;
    this->target_y = target_y;
    this->direction = direction;
    this->speed_driver = speed_driver;
    this->precision_params = precision_params;
}

void Move_Straight::compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params)
{
    // Compute the distance to travel
    float distance = Point::distance(current_point, Point(this->target_x, this->target_y)) * (*this->direction);

    // Create the step action
    this->step_action = new Step_Forward_Backward(distance, this->speed_driver, this->precision_params);

    // Compute the step action
    this->step_action->compute(current_ticks, rolling_basis_params);
    this->is_computed = true;
}

// Get Orientation in front of a point (turn on itself)
Get_Orientation::Get_Orientation(float target_x, float target_y, Direction *direction, Speed_Driver *speed_driver, Precision_Params *precision_params)
{
    this->target_x = target_x;
    this->target_y = target_y;
    this->direction = direction;
    this->speed_driver = speed_driver;
    this->precision_params = precision_params;
}

void Get_Orientation::compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params)
{   
    // Compute the angle to turn
    float theta_dif = Point::angle(Point(this->target_x, this->target_y), current_point);
    float theta = fmod((theta_dif - current_point.theta + PI), (2 * PI));

    // Add PI rad if the direction is backward
    if ((*this->direction) == backward)
        theta += PI;
    
     //Check if the angle is greater than PI
    if (theta > PI)
    {
        //adjust the directun, turn to the left
        theta -= (2* PI); 
    }
    
    // Create the step action
    this->step_action = new Step_Rotation(theta, this->speed_driver, this->precision_params);

    // Compute the step action
    this->step_action->compute(current_ticks, rolling_basis_params);
    this->is_computed = true;
}

// Do a Rotation (turn on itself)
Move_Rotation::Move_Rotation(float target_theta, Direction *direction, Speed_Driver *speed_driver, Precision_Params *precision_params)
{   
    this->target_theta = target_theta;
    this->direction = direction;
    this->speed_driver = speed_driver;
    this->precision_params = precision_params;
}

void Move_Rotation::compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params)
{
    // Get the current robot angle (between 0 and 2PI)
    float mod_current_theta = fmod(current_point.theta, 2.0 * PI);

    if ((*this->direction) == backward)
        mod_current_theta += PI;

    // Compute angle to turn
    float delta_theta = this->target_theta - mod_current_theta;

    // Create the step action
    this->step_action = new Step_Rotation(delta_theta, this->speed_driver, this->precision_params);

    // Compute the step action
    this->step_action->compute(current_ticks, rolling_basis_params);
    this->is_computed = true;
}
