#include <Arduino.h>
#include "basic_actions.h"

class Complex_Action
{
public:
    Movement_Params params;
    byte speed;
    direction dir;

    Basic_Movement **basic_actions;
    short basic_actions_list_size;
    
    action_state state = not_started;
    short action_index = 0;
    bool is_computed = false;
    void handle(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Motor *right_motor, Motor *left_motor, Rolling_Basis_Params *rolling_basis_params);
    virtual void compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params) = 0;
    bool is_finished();
    void alloc_memory(short nb_actions);
};

class Go_To : public Complex_Action
{
public:
    float target_x, target_y; 
    Go_To(float target_x, float target_y, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision);
    void compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};


class Curve_Go_To : public Complex_Action
{
public:
    float target_x, target_y, circle_center_x, circle_center_y;
    int ticks_interval;
    Curve_Go_To(float target_x, float target_y, float circle_center_x, float circle_center_y, int ticks_interval, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision);
    void compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};
