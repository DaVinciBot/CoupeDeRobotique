#include <complex_action.h>

// Complex deplacement action generic class
void Complex_Action::alloc_memory(short nb_actions)
{
    this->nb_basic_movements = nb_actions;
    this->basic_movements = new Basic_Action *[nb_actions];
}

void Complex_Action::handle(Point current_point, Ticks current_ticks, Rolling_Basis_Ptrs *rolling_basis_ptrs)
{
    // Compute the complex action
    if (!this->is_computed)
        this->compute(
            current_point,
            current_ticks,
            rolling_basis_ptrs->rolling_basis_params
        );

    // Handle the complex action
    if (0 <= this->movement_index && this->movement_index < this->nb_basic_movements)
    {
        this->state = in_progress;
        // Handle basic action
        if (
                this->basic_movements[this->movement_index]->state == not_started ||
                this->basic_movements[this->movement_index]->state == in_progress
            )   
            this->basic_movements[this->movement_index]->handle(
                current_point,
                current_ticks,
                rolling_basis_ptrs
            );
        
        // End of the basic action
        else if (this->basic_movements[this->movement_index]->is_finished())
            this->movement_index++;  
    }
    else
        this->state = finished;
}

// Simple action for going to a point
Go_To::Go_To(Point target_point, Direction direction, Speed_Driver speed_driver, Precision_Params precision_params)
{
    this->target_point = target_point;
    this->direction = direction;
    this->speed_driver = speed_driver;
    this->precision_params = precision_params;
}

bool Go_To::operator==(Complex_Action &other)
{
    if (other.get_id() != GO_TO)
        return false;

    Go_To *other_go_to = (Go_To *)&other;
    return this->target_point == other_go_to->target_point && this->direction == other_go_to->direction && !memcmp(&this->precision_params, &other_go_to->precision_params, sizeof(Precision_Params));
}
void Go_To::compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params)
{
    //  Go to is simple move
    //  1°) rotate to be in front of the target point
    //  2°) go to the target point
    this->alloc_memory(2);

    // Define fix params for rotation 
    static Precision_Params orientation_precision_params{100, 10, 20};
    static Speed_Driver_From_Distance orientation_speed_driver(140, 0, 140, 0, 140, 0);
    
    this->basic_movements[0] = new Get_Orientation(
        this->target_point.x, this->target_point.y,
        &this->direction,
        &orientation_speed_driver,
        &orientation_precision_params
    );

    this->basic_movements[1] = new Move_Straight(
        this->target_point.x, this->target_point.y,
        &this->direction,
        &this->speed_driver,
        &this->precision_params
    );
    this->is_computed = true;
}

// Action for going to a point with a curve
Curve_Go_To::Curve_Go_To(Point target_point, Point center_point, unsigned short interval, Direction direction, Speed_Driver speed_driver, Precision_Params precision_params)
{
    this->target_point = target_point;
    this->center_point = center_point;
    this->interval = interval;
    this->direction = direction;
    this->speed_driver = speed_driver;
    this->precision_params = precision_params;
}

bool Curve_Go_To::operator==(Complex_Action &other)
{
    if (other.get_id() != CURVE_GO_TO)
        return false;

    Curve_Go_To *other_curve_go_to = (Curve_Go_To *)&other;
    return this->target_point == other_curve_go_to->target_point && this->center_point == other_curve_go_to->center_point && this->interval == other_curve_go_to->interval && this->direction == other_curve_go_to->direction && !memcmp(&this->precision_params, &other_curve_go_to->precision_params, sizeof(Precision_Params));
}

void Curve_Go_To::compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params)
{
    // Calcul the radius of the circle
    float radius = Point::distance(this->center_point, this->target_point);

    // Get the angle of the target point and the current point
    float target_angle = atan2(this->target_point.y - this->center_point.y, this->target_point.x - this->center_point.x);
    float current_angle = atan2(current_point.y - this->center_point.y, current_point.x - this->center_point.x);

    float dif_angle = target_angle - current_angle;
    float distance = radius * dif_angle;

    // Calcul nb of points on the trajectory
    int nb_points = abs(distance / this->interval);
    this->alloc_memory(nb_points * 2);

    for (int k = 0; k < nb_points; k+=2)
    {
        // Calcul the coordonates of the point
        float x = this->center_point.x + radius * cos(current_angle + k * dif_angle / nb_points);
        float y = this->center_point.y + radius * sin(current_angle + k * dif_angle / nb_points);

        this->basic_movements[k] = new Get_Orientation(
                x, y,
                &this->direction,
                &this->speed_driver,
                &this->precision_params
            );
        this->basic_movements[k+1] = new Move_Straight(
                x, y,
                &this->direction,
                &this->speed_driver,
                &this->precision_params
            );
    }
    this->is_computed = true;
}
