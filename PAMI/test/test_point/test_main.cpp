#include <unity.h>

#include "arduino_compat.h"
#include "point.h"

void setUp() {}
void tearDown() {}

void test_point_distance() {
    Point origin(0.0f, 0.0f, 0.0f);
    Point north(0.0f, 100.0f, 0.0f);

    TEST_ASSERT_FLOAT_WITHIN(0.001f, 100.0f, Point::distance(origin, north));
}

void test_point_angle() {
    Point origin(0.0f, 0.0f, 0.0f);
    Point north(0.0f, 100.0f, 0.0f);

    TEST_ASSERT_FLOAT_WITHIN(0.001f, PI / 2.0f, Point::angle(origin, north));
}

int main(int argc, char** argv) {
    UNITY_BEGIN();
    RUN_TEST(test_point_distance);
    RUN_TEST(test_point_angle);
    return UNITY_END();
}
