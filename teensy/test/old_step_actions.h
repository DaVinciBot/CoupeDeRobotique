#include <Arduino.h>
#include <motors_driver.h>

typedef enum
{
    not_started,
    in_progress,
    finished
} action_state;
typedef enum
{
    forward = 1,
    backward = -1,
} direction;

typedef enum
{
    clockwise,
    counterclockwise,
} sens;

struct Movement_Params
{
    unsigned int end_movement_presicion;
    unsigned int error_precision;
    unsigned int trajectory_precision;
};

struct Rolling_Basis_Params
{
    int encoder_resolution;
    float wheel_perimeter;
    float radius;
};

class Step_Movement
{
    public:
        action_state state = not_started;
        unsigned int end_movement_cpt = 0;

        Movement_Params params;

        long total_ticks;
        long ticks_cursor = 0;

        long right_ref;
        long left_ref;
        short right_sign = 1;
        short left_sign = 1;

        byte speed;

        bool is_computed = false;

        virtual void compute(long right_ticks, long left_ticks, int encoder_resolution, float wheel_perimeter, float radius);
        void check_end_of_action(long current_right_ticks, long current_left_ticks);
        void update_action_cursor(long current_right_ticks, long current_left_ticks);
        void handle(long current_right_ticks, long current_left_ticks, Motor * right_motor, Motor * left_motor);
        bool is_finished();
};

class Step_Forward_Backward : public Step_Movement
{
    public:
        direction dir;
        float distance;
        Step_Forward_Backward(float distance, byte speed, Movement_Params params);
        void compute(long current_right_ticks, long current_left_ticks, int encoder_resolution, float wheel_perimeter, float radius) override;
};

class Step_Rotation : public Step_Movement
{
    public:
        sens rotation_dir;
        float theta;
        Step_Rotation(float theta, byte speed, Movement_Params params);
        void compute(long current_right_ticks, long current_left_ticks, int encoder_resolution, float wheel_perimeter, float radius) override;
};
