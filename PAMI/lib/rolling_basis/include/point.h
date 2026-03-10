#pragma once
#include <math.h>

/**
 * @brief Class representing a point in 2D space with orientation.
 *
 */
class Point {
   public:
    float x = 0.0f;      // X coordinate in millimeters
    float y = 0.0f;      // Y coordinate in millimeters
    float theta = 0.0f;  // Orientation in radians

    Point() = default;

    /**
     * @brief Construct a new Point object
     *
     * @param x X coordinate in millimeters
     * @param y Y coordinate in millimeters
     * @param theta Orientation in radians (default: 0.0f)
     */
    Point(float x, float y, float theta = 0.0f) {
        this->x = x;
        this->y = y;
        this->theta = theta;
    }

    /**
     * @brief Assignment operator
     *
     * @param other  Point to copy from
     * @return Point&
     */
    Point& operator=(const Point& other) {
        if (this != &other) {
            x = other.x;
            y = other.y;
            theta = other.theta;
        }
        return *this;
    }

    /**
     * @brief Equality operator
     *
     * @param other Point to compare with
     * @return true
     * @return false
     */
    bool operator==(const Point& other) {
        return x == other.x && y == other.y && theta == other.theta;
    }

    /**
     * @brief Calculate the Euclidean distance in millimeters between two points
     *
     * @param p1 First point
     * @param p2 Second point
     * @return float
     */
    static float distance(Point p1, Point p2) {
        return sqrtf(pow(p2.x - p1.x, 2) + pow(p2.y - p1.y, 2));
    }
    /**
     * @brief Calculate the angle in radians from p1 to p2
     *
     * @param p1 First point
     * @param p2 Second point
     * @return double
     */
    static double angle(const Point& p1, const Point& p2) {
        return atan2f(p2.y - p1.y, p2.x - p1.x);
    }
};
