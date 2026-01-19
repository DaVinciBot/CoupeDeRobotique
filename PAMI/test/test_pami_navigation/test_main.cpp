#include <unity.h>

#include "arduino_compat.h"
#include "motor.h"
#include "navigation.h"
#include "point.h"
#include "rolling_basis.h"

void setUp() {
    resetFakeTime();
}
void tearDown() {}

void test_navigation_initialization() {
    Motor left(1, 2, 3, 400, 500, false);
    Motor right(4, 5, 6, 400, 500, false);
    left.init();
    right.init();
    
    RollingBasis basis(&left, &right, 60.0f, 132.0f);
    Navigation nav(&basis, 5000);  // 5 second timeout

    TEST_ASSERT_FALSE(nav.isMoving());
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.0f, nav.getPose().x);
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.0f, nav.getPose().y);
}

void test_navigation_forward_command() {
    Motor left(7, 8, 9, 400, 500, false);
    Motor right(10, 11, 12, 400, 500, false);
    left.init();
    right.init();
    
    RollingBasis basis(&left, &right, 60.0f, 132.0f);
    Navigation nav(&basis, 5000);

    Point target(100.0f, 0.0f, 0.0f);  // forward motion
    nav.setCommand(target);

    TEST_ASSERT_TRUE(nav.isMoving());
    nav.update();
    TEST_ASSERT_TRUE(nav.isMoving());
}

void test_navigation_lateral_command() {
    Motor left(13, 14, 15, 400, 500, false);
    Motor right(16, 17, 18, 400, 500, false);
    left.init();
    right.init();
    
    RollingBasis basis(&left, &right, 60.0f, 132.0f);
    Navigation nav(&basis, 5000);

    Point target(0.0f, 100.0f, 0.0f);  // lateral motion (requires rotation)
    nav.setCommand(target);

    TEST_ASSERT_TRUE(nav.isMoving());
    nav.update();
    TEST_ASSERT_TRUE(nav.isMoving());
}

void test_navigation_stop() {
    Motor left(19, 20, 21, 400, 500, false);
    Motor right(22, 23, 24, 400, 500, false);
    left.init();
    right.init();
    
    RollingBasis basis(&left, &right, 60.0f, 132.0f);
    Navigation nav(&basis, 5000);

    Point target(100.0f, 0.0f, 0.0f);
    nav.setCommand(target);
    TEST_ASSERT_TRUE(nav.isMoving());

    nav.stop();
    TEST_ASSERT_FALSE(nav.isMoving());
}

void test_navigation_timeout() {
    Motor left(25, 26, 27, 400, 500, false);
    Motor right(28, 29, 30, 400, 500, false);
    left.init();
    right.init();
    
    RollingBasis basis(&left, &right, 60.0f, 132.0f);
    Navigation nav(&basis, 1000);  // 1 second timeout

    // Advance time so _startMs won't be 0
    advanceFakeMicros(1000);

    Point target(100.0f, 0.0f, 0.0f);
    nav.setCommand(target);
    TEST_ASSERT_TRUE(nav.isMoving());

    // Advance time and update
    advanceFakeMicros(500000);  // 500 ms
    nav.update();
    TEST_ASSERT_TRUE(nav.isMoving());

    // Advance time past timeout
    advanceFakeMicros(600000);  // 600 ms more (total > 1 second)
    nav.update();
    
    // Now should be stopped due to timeout
    TEST_ASSERT_FALSE(nav.isMoving());
}

void test_navigation_get_pose() {
    Motor left(31, 32, 33, 400, 500, false);
    Motor right(34, 35, 36, 400, 500, false);
    left.init();
    right.init();
    
    RollingBasis basis(&left, &right, 60.0f, 132.0f);
    Navigation nav(&basis, 5000);

    Point target(50.0f, 50.0f, 0.0f);
    nav.setCommand(target);

    Point pose = nav.getPose();
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.0f, pose.x);
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.0f, pose.y);
}

void test_navigation_diagonal_motion() {
    Motor left(37, 38, 39, 400, 500, false);
    Motor right(40, 41, 42, 400, 500, false);
    left.init();
    right.init();
    
    RollingBasis basis(&left, &right, 60.0f, 132.0f);
    Navigation nav(&basis, 5000);

    Point target(100.0f, 100.0f, 0.0f);  // diagonal motion
    nav.setCommand(target);

    TEST_ASSERT_TRUE(nav.isMoving());
    nav.update();
    TEST_ASSERT_TRUE(nav.isMoving());
}

int main(int argc, char** argv) {
    UNITY_BEGIN();
    RUN_TEST(test_navigation_initialization);
    RUN_TEST(test_navigation_forward_command);
    RUN_TEST(test_navigation_lateral_command);
    RUN_TEST(test_navigation_stop);
    RUN_TEST(test_navigation_timeout);
    RUN_TEST(test_navigation_get_pose);
    RUN_TEST(test_navigation_diagonal_motion);
    return UNITY_END();
}