#include <Arduino.h>
#include <step_actions.h>

class Basic_Movement
{
    public:
        action_state state = not_started;
        Step_Movement * step_action;
        Movement_Params params;
        direction dir;
        byte speed;
        bool is_computed = false;
        virtual void compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params) = 0;
        void handle(long current_right_ticks, long current_left_ticks, Motor *right_motor, Motor *left_motor);
        bool is_finished();

};

class Move_Straight : public Basic_Movement
{
    public:
        float target_x, target_y;
        Move_Straight(float target_x, float target_y, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision);
        void compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};

class Get_Orientation : public Basic_Movement
{
    public:
        float target_x, target_y;
        Get_Orientation(float target_x, float target_y, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision);
        void compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};

class Move_Rotation : public Basic_Movement
{
    public:
        float target_theta;
        Move_Rotation(float target_tetha, direction dir, byte speed, unsigned int end_movement_presicion, unsigned int error_precision, unsigned int trajectory_precision);
        void compute(float current_x, float current_y, float current_theta, long current_right_ticks, long current_left_ticks, Rolling_Basis_Params *rolling_basis_params) override;
};