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
    // angle = 2 * atan2(‖u/‖u‖ − v/‖v‖‖, ‖u/‖u‖ + v/‖v‖‖)
    static double angle(const Point &p1, const Point &p2)
    {
        // return atan2(p2.y - p1.y, p2.x - p1.x);
        double norm_u = std::hypot(p1.x, p1.y);
        double norm_v = std::hypot(p2.x, p2.y);
        if (norm_u == 0.0 || norm_v == 0.0) {
            return 0.0;
        }

        double ux = p1.x / norm_u;
        double uy = p1.y / norm_u;
        double vx = p2.x / norm_v;
        double vy = p2.y / norm_v;

        double dx = ux - vx;
        double dy = uy - vy;
        double sx = ux + vx;
        double sy = uy + vy;

        return 2.0 * std::atan2(
            std::hypot(dx, dy),
            std::hypot(sx, sy)
        );
    }
};