#include <math.h>

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