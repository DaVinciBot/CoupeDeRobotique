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
    virtual inline byte get_id() {return 0;} // Return the id of the action (usefull for Com), not obligatory implemented on childs classes
    bool is_finished();
    
    // Constructor / Destructor
    Action() = default;
    virtual ~Action() = default;

    // Method(s)
    virtual void handle(Point current_point, Ticks current_ticks, Rolling_Basis_Ptrs *rolling_basis_ptrs) = 0;
};