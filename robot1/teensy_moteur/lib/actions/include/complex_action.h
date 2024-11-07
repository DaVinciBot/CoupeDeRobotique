#include <basic_action.h>
#include <commands.h>

// Complex deplacement action generic class
class Complex_Action : public Action
{
public:
    // Values for speed, precision, ... are constant throughout the trajectory, 
    // so they are only stored in the high-level class; 
    // lower-level classes access them via pointers
    
    // Operators
    virtual bool operator==(Complex_Action &other) = 0;

    // Atributes
    // Trajectory parameters
    Precision_Params precision_params;
    Direction direction;
    Speed_Driver speed_driver;

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
    // Property
    inline byte get_id() { return GO_TO; }

    // Operators
    bool operator==(Complex_Action &other);

    // Atribute
    Point target_point;

    // Constructor
    Go_To(Point target_point, Direction direction, Speed_Driver speed_driver, Precision_Params precision_params);

    // Method
    void compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params);
};

// Action for going to a point with a curve
class Curve_Go_To : public Complex_Action
{
public:
    // Property
    inline byte get_id() { return CURVE_GO_TO; }

    // Operators
    bool operator==(Complex_Action &other);

    // Atributes
    Point target_point, center_point;
    unsigned short interval;

    // Constructor
    Curve_Go_To(Point target_point, Point center_point, unsigned short interval, Direction direction, Speed_Driver speed_driver, Precision_Params precision_params);

    // Method
    void compute(Point current_point, Ticks current_ticks, Rolling_Basis_Params *rolling_basis_params);
};



