#include <action.h>

bool Action::is_finished(){
    return this->state == finished;
}