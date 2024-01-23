#include <Arduino.h>
//#include <motors_driver.h>
#include <speed_driver.h>

// Generic action class
class Action {
public:
    // Atributes
    bool is_computed = false;
    Action_state state = not_started;
    
    // Propertie(s)
    bool is_finished();

    // Constructor
    Action() = default;

    // Method(s)
    virtual void handle(Point current_point, Ticks current_ticks, Rolling_Basis_Ptrs *rolling_basis_ptrs) = 0;
};