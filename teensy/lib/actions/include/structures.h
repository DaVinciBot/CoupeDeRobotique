typedef enum
{
    not_started,
    in_progress,
    finished
} Action_state;
typedef enum
{
    forward = 1,
    backward = -1,
} Direction;

typedef enum
{
    clockwise,
    counterclockwise,
} Sens;

struct Precision_Params
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

struct Rolling_Basis_Ptrs
{
    Rolling_Basis_Params *rolling_basis_params;
    Motor *right_motor;
    Motor *left_motor;
};

struct Ticks
{
    long right;
    long left;
};

class Point
{
public:
    float x = -1.0f;
    float y = -1.0f;
    float theta = -1.0f;

    Point() = default; 

    Point(float x, float y, float theta = 1234.1234f)
    {
        this->x = x;
        this->y = y;
        this->theta = theta;
    }

    Point &operator=(const Point &other)
    {
        if (this != &other)
        {
            x = other.x;
            y = other.y;
            theta = other.theta;
        }
        return *this;
    }

    static float distance(Point p1, Point p2)
    {
        return sqrt(pow(p2.x - p1.x, 2) + pow(p2.y - p1.y, 2));
    }
    static float angle(Point p1, Point p2)
    {
        return atan2(p2.y - p1.y, p2.x - p1.x);
    }
};

struct Profil_params
{
    byte offset;
    float gamma; // Gamma is the slope of the affine line representing the acceleration profile
    float distance;
};

/*
struct Profil_params
{
    byte offset;
    float gamma; // Gamma is the slope of the affine line representing the acceleration profile
    float distance;
};

class Speed_Driver
{
    // How to use speed Driver:
    // Give gamma and offset
    // 2 cases:
    // 1°) Give Gamma value, it will be directly use to compute the speed (use Speed_Driver_From_Gamma class)
    // speed = gamma * ticks + offset (speed <= max_speed)
    // 2°) Give distance_to_max_speed, it will be use to compute gamma (use Speed_Driver_From_Distance class)
    // The distance_to_max_speed has to be given in cm, when the compute function will be
    // called, the encoder_resolution and wheel_perimeter will be used to convert it in ticks
    // Gamma = (max_speed - offset) / (distance_to_max_speed * encoder_resoltion / wheel_perimeter)
public:
    // Attributes
    byte max_speed;
    long end_ticks;
    bool correction = false;

    // Acceleration params
    Profil_params acceleration_params = {0, -1.0f, -1.0f};

    // Deceleration params
    Profil_params deceleration_params = {0, -1.0f, -1.0f};

    

    Speed_Driver() = default;

    // Methodes
    void compute_acceleration_profile(Rolling_Basis_Params *rolling_basis_params, long end_ticks)
    {
        this->end_ticks = end_ticks;

        // Compute acceleration profile
        if (this->acceleration_params.gamma == -1.0f)
        {
            byte y_delta = this->max_speed - this->acceleration_params.offset;
            float distance_to_max_speed_ticks = (this->acceleration_params.distance * rolling_basis_params->encoder_resolution) / rolling_basis_params->wheel_perimeter;
            this->acceleration_params.gamma = (float)y_delta / distance_to_max_speed_ticks;
        }

        // Compute deceleration profile
        if (this->deceleration_params.gamma == -1.0f)
        {
            byte y_delta = this->max_speed - this->deceleration_params.offset; 
            float distance_to_speed_down_ticks = this->end_ticks - (this->deceleration_params.distance * rolling_basis_params->encoder_resolution) / rolling_basis_params->wheel_perimeter;
            this->deceleration_params.gamma = (float)y_delta / distance_to_speed_down_ticks; // Negative because we want to decelerate
        }
    }

    byte compute_local_speed(long ticks)
    {
        // Calcul des points de changement de vitesse (acceleration -> plateau -> deceleration)
        long debut_plateau_ticks = (this->max_speed - this->acceleration_params.offset) / this->acceleration_params.gamma;
        long fin_plateau_ticks = ((this->max_speed - this->deceleration_params.offset) / this->deceleration_params.gamma) + this->end_ticks;

        byte speed = 0;
        // On verifie qu'il y a un plateau
        if (debut_plateau_ticks < fin_plateau_ticks)
        {
            // On est dans la phase d'acceleration
            if (ticks < debut_plateau_ticks)
                speed = (byte)(this->acceleration_params.gamma * ticks + this->acceleration_params.offset);
            
            // On est dans la phase de plateau
            else if (ticks < fin_plateau_ticks)
                speed =  this->max_speed;
            
            // On est dans la phase de deceleration
            else
                speed = (byte)(this->deceleration_params.gamma * (ticks - this->end_ticks) + this->deceleration_params.offset);
        }
        // Pas de plateau
        else
        {
            // Calcul du point d'intersection de l'accélération et de la décélération
            long intersection_ticks = (this->deceleration_params.offset - this->acceleration_params.offset - (this->deceleration_params.gamma * this->end_ticks)) / (this->acceleration_params.gamma - this->deceleration_params.gamma);

            // phase acceleration
            if(ticks < intersection_ticks)
                speed = (byte)(this->acceleration_params.gamma * ticks + this->acceleration_params.offset);
            
            // phase deceleration
            else
                speed = (byte)(this->deceleration_params.gamma * (ticks - this->end_ticks) + this->deceleration_params.offset);
        }

        if (this->correction)
        {                 
            this->correction = false;
            return 80;
        }
        return speed;
    }
};

class Speed_Driver_From_Gamma : public Speed_Driver
{
public:
    // We only need to give gamma and offset, the distance is not used in this case (it's set to -1.0f by default and will be ingored if given)
    Speed_Driver_From_Gamma(byte max_speed, Profil_params acceleration, Profil_params deceleration)
    {
        this->max_speed = max_speed;

        // Acceleration params
        this->acceleration_params.offset = acceleration.offset;
        this->acceleration_params.gamma = acceleration.gamma;
        
        // Deceleration params
        this->deceleration_params.offset = deceleration.offset;
        this->deceleration_params.gamma = deceleration.gamma;
    }
};

class Speed_Driver_From_Distance : public Speed_Driver
{
public:
    // We only need to give distance and offset, the gamma is not used in this case (it's set to -1.0f by default and will be ingored if given)
    Speed_Driver_From_Distance(byte max_speed, Profil_params acceleration, Profil_params deceleration)
    {
        this->max_speed = max_speed;

        // Acceleration params
        this->acceleration_params.offset = acceleration.offset;
        this->acceleration_params.distance = acceleration.distance;
        
        // Deceleration params
        this->deceleration_params.offset = deceleration.offset;
        this->deceleration_params.distance = deceleration.distance;
    }
};
*/