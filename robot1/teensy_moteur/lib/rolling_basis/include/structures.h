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

    bool operator==(const Point &other)
    {
        return x == other.x && y == other.y && theta == other.theta;
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
    float distance;

    float a; // Propotionnal offset
    float p; // Variation strenght
    float b; // Center to 0
    float c; // Slope
};