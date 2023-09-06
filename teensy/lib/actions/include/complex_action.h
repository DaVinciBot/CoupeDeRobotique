#include <basic_action.h>

// Complex deplacement action generic class
class Complex_Action : public Action
{
public:
    // Values for speed, precision, ... are constant throughout the trajectory, 
    // so they are only stored in the high-level class; 
    // lower-level classes access them via pointers
    
    // Atributes
    // Trajectory parameters
    Precision_Params precision_params;
    Direction direction;
    byte speed;

    Basic_Action **basic_movements;
    short nb_basic_movements;
    short movement_index = 0;

    // Constructor
    Complex_Action() = default;

    // Methods
    void alloc_memory(short nb_actions);
    virtual void compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params) = 0;
    void handle(Point current_point, Ticks current_ticks, Rolling_Basis_Ptrs *rolling_basis_ptrs) override;
};

// Simple action for going to a point
class Go_To : public Complex_Action
{
public:
    // Atribute
    Point target_point;

    // Constructor
    Go_To(Point target_point, Direction direction, byte speed, Precision_Params precision_params);
    
    // Method
    void compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params);
};

// Action for going to a point with a curve
class Curve_Go_To : public Complex_Action
{
public:
    // Atributes
    Point target_point, center_point;
    unsigned short interval;

    // Constructor
    Curve_Go_To(Point target_point, Point center_point, unsigned short interval, Direction direction, byte speed, Precision_Params precision_params);

    // Method
    void compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params);
};



