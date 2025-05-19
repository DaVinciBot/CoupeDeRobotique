class Point
{
public:
    double x = -1.0f;
    double y = -1.0f;
    double theta = -1.0f;

    Point() = default;

    Point(double x, double y, double theta = 1234.1234)
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