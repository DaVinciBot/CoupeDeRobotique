#include <step_action.h>

// Basic deplacement action generic class
class Basic_Action : public Action
{
public:
    // Values for speed, precision, ... are constant throughout the trajectory,
    // so they are only stored in the high-level class;
    // lower-level classes access them via pointers

    // Atributes
    // Trajectory parameters
    Precision_Params *precision_params;
    byte *speed;
    Direction *direction;

    Step_Action *step_action;

    // Constructor
    Basic_Action() = default;

    // Methods
    virtual void compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params) = 0;
    void handle(Point current_point, Ticks current_ticks, Rolling_Basis_Ptrs *rolling_basis_ptrs) override;
};

// This basic action going straight by the distance between its current position
// and the target position, it will not rotate ensure you are correctly oriented
// before using it 
class Move_Straight : public Basic_Action
{
public:
    // Atributes
    float target_x, target_y;

    // Constructor
    Move_Straight(float target_x, float target_y, Direction* direction, byte* speed,Precision_Params *precision_params);

    // Method
    void compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};

// This basic action turns the robot to face the target point
// Get Orientation in front of a point (turn on itself)
class Get_Orientation : public Basic_Action
{
public:
    // Atributes
    float target_x, target_y;

    // Constructor
    Get_Orientation(float target_x, float target_y, Direction *direction, byte *speed, Precision_Params *precision_params);

    // Method
    void compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};

// This basic action will rotate the robot to the target angle
// Do a Rotation (turn on itself)
class Move_Rotation : public Basic_Action
{
public:
    // Atribute
    float target_theta;

    // Constructor
    Move_Rotation(float target_theta, Direction *direction, byte *speed, Precision_Params *precision_params);

    // Method
    void compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};