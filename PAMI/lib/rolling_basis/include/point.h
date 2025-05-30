#include <math.h>

class Point
{
public:
    float x = 0.0f;
    float y = 0.0f;
    float theta = 0.0f;

    Point() = default;

    Point(float x, float y, float theta = 0.0f)
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
        return sqrtf(pow(p2.x - p1.x, 2) + pow(p2.y - p1.y, 2));
    }
    static double angle(const Point &p1, const Point &p2)
    {
        return atan2f(p2.y - p1.y, p2.x - p1.x);
    }
};