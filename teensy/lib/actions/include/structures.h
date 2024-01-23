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
    byte offset;
    float gamma = -1.0f; // Gamma is the slope of the affine line representing the acceleration profile
    float distance_to_max_speed = -1.0f;
    long end_ticks;

    Speed_Driver() = default;

    // Methodes
    void compute_acceleration_profile(Rolling_Basis_Params *rolling_basis_params, long end_ticks)
    {
        this->end_ticks = end_ticks;

        if (this->gamma == -1.0f)
        {
            byte y_delta = this->max_speed - this->offset;
            float distance_to_max_speed_ticks = (this->distance_to_max_speed * rolling_basis_params->encoder_resolution) / rolling_basis_params->wheel_perimeter;
            this->gamma = (float)y_delta / distance_to_max_speed_ticks;
        }
    }

    /*byte compute_local_speed(long ticks)
    {
        byte local_speed = (byte)(this->gamma * ticks + this->offset);
        return (local_speed > this->max_speed) ? this->max_speed : local_speed;
    }*/
    byte compute_local_speed(long ticks)
    {
        // Calculer la progression du mouvement en tant que ratio
        float progress = (float)ticks / this->end_ticks;

        // Ajuster gamma pour l'accélération et la décélération
        // Utilisation d'une fonction comme une parabole inversée pour la progression
        float adjusted_gamma = this->gamma * (1 - 4 * (progress - 0.5) * (progress - 0.5));

        // Calculer la vitesse locale
        byte local_speed = (byte)(adjusted_gamma * ticks + this->offset);

        // Limiter la vitesse à max_speed
        return (local_speed > this->max_speed) ? this->max_speed : local_speed;
    }

    float get_gamma()
    {
        return this->gamma;
    }
};

class Speed_Driver_From_Gamma : public Speed_Driver
{
public:
    Speed_Driver_From_Gamma(byte max_speed, byte offset, float gamma)
    {
        this->max_speed = max_speed;
        this->offset = offset;
        this->gamma = gamma;
    }
};

class Speed_Driver_From_Distance : public Speed_Driver
{
public:
    Speed_Driver_From_Distance(byte max_speed, byte offset, float distance_to_max_speed)
    {
        this->max_speed = max_speed;
        this->offset = offset;
        this->distance_to_max_speed = distance_to_max_speed;
    }
};
