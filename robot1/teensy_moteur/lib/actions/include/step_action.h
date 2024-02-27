#include <action.h>

// Step motor action generic class
class Step_Action : public Action
{
public:
    // Values for speed, precision, ... are constant throughout the trajectory,
    // so they are only stored in the high-level class;
    // lower-level classes access them via pointers

    // Trajectory parameters
    Precision_Params *precision_params;
    Speed_Driver *speed_driver;

    long total_ticks;
    long ticks_cursor = 0;

    long right_ref;
    long left_ref;
    short right_sign = 1;
    short left_sign = 1;

    unsigned int end_movement_cpt = 0;

    // Constructor
    Step_Action() = default;

    // Methods
    void check_end_of_action(Ticks current_ticks);
    void update_action_cursor(Ticks current_ticks);

    virtual void compute(Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params) = 0;
    void handle(Point current_point, Ticks current_ticks, Rolling_Basis_Ptrs *rolling_basis_ptrs) override;
};

// Move Forward or Backward 
class Step_Forward_Backward : public Step_Action
{
public:
    // Atributes
    float distance;
    Direction direction;

    // Constructor
    Step_Forward_Backward(float distance, Speed_Driver *speed_driver, Precision_Params *precision_params);

    // Method
    void compute(Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};

// Do a rotation (turn on itself)
class Step_Rotation : public Step_Action
{
public:
    // Attributes
    float theta;
    Sens rotation_sens;

    // Constructor
    Step_Rotation(float theta, Speed_Driver *speed_driver, Precision_Params *precision_params);

    // Method
    void compute(Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};
