#include <unity.h>

#include "arduino_compat.h"
#include "motor.h"
#include "pid.h"
#include "point.h"
#include "rolling_basis.h"

void setUp() {
    resetFakeTime();
}
void tearDown() {}

void test_motor_scaling_and_enable() {
    Motor motor(1, 2, 3, 400, 500, false);
    motor.init();

    motor.setAcceleration(2.0f);  // -> 200 steps/s^2 after internal scaling
    motor.setTargetSpeed(3.5f);   // -> 3500 steps/s after internal scaling

    TEST_ASSERT_TRUE(motor.isMoving());
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 200.0f, motor.getAccelerationForTest());
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 3500.0f,
                             motor.getTargetSpeedStepsPerSecForTest());
}

void test_motor_acceleration_ramp_and_steps() {
    Motor motor(4, 5, 6, 400, 500, false);
    motor.init();
    motor.setAcceleration(1.0f);  // -> 100 steps/s^2
    motor.setTargetSpeed(5.0f);   // -> 5000 steps/s

    advanceFakeMicros(50000);  // 50 ms
    motor.update();
    TEST_ASSERT_FLOAT_WITHIN(0.5f, 5.0f,
                             motor.getCurrentSpeedStepsPerSecForTest());

    advanceFakeMicros(50000);  // another 50 ms
    motor.update();
    TEST_ASSERT_FLOAT_WITHIN(0.5f, 10.0f,
                             motor.getCurrentSpeedStepsPerSecForTest());

    advanceFakeMicros(200000);  // ramp a bit more and allow a step to occur
    motor.update();
    TEST_ASSERT_TRUE(motor.getStepCount() > 0);
}

void test_point_distance_and_angle() {
    Point origin(0.0f, 0.0f, 0.0f);
    Point north(0.0f, 100.0f, 0.0f);

    TEST_ASSERT_FLOAT_WITHIN(0.001f, 100.0f, Point::distance(origin, north));
    TEST_ASSERT_FLOAT_WITHIN(0.001f, PI / 2.0f, Point::angle(origin, north));
}

void test_rolling_basis_forward_motion() {
    Motor left(7, 8, 9, 400, 500, false);
    Motor right(10, 11, 12, 400, 500, false);
    RollingBasis basis(&left, &right, 60.0f, 132.0f);

    basis.setCommand(Point(100.0f, 0.0f, 0.0f));  // straight forward

    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.0f, basis.getRotateDurationForTest());
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 5.0f, basis.getForwardDurationForTest());

    basis.update();
    TEST_ASSERT_EQUAL(RollingBasis::Phase::Forwarding, basis.getPhaseForTest());

    const float circumference = static_cast<float>(PI) * 60.0f;
    const float expectedWheelSteps =
        (20.0f / circumference) * left.getStepsPerRev() * 1000.0f;

    TEST_ASSERT_FLOAT_WITHIN(1.0f, expectedWheelSteps,
                             left.getTargetSpeedStepsPerSecForTest());
    TEST_ASSERT_FLOAT_WITHIN(1.0f, expectedWheelSteps,
                             right.getTargetSpeedStepsPerSecForTest());
}

void test_rolling_basis_rotation_then_forward() {
    Motor left(13, 14, 15, 400, 500, false);
    Motor right(16, 17, 18, 400, 500, false);
    RollingBasis basis(&left, &right, 60.0f, 132.0f);

    basis.setCommand(Point(0.0f, 100.0f, 0.0f));  // requires a 90° rotation

    TEST_ASSERT_EQUAL(RollingBasis::Phase::Rotating, basis.getPhaseForTest());

    // During rotation the wheel speeds should be symmetric with opposite signs
    advanceFakeMicros(500000);  // 0.5 s < rotate duration
    basis.update();

    const float circumference = static_cast<float>(PI) * 60.0f;
    const float halfBase = 132.0f * 0.5f;
    const float expectedWheel =
        (basis.getAngularSpeedRadPerS() * halfBase / circumference) *
        left.getStepsPerRev() * 1000.0f;

    TEST_ASSERT_FLOAT_WITHIN(2.0f, expectedWheel,
                             right.getTargetSpeedStepsPerSecForTest());
    TEST_ASSERT_FLOAT_WITHIN(2.0f, -expectedWheel,
                             left.getTargetSpeedStepsPerSecForTest());

    // After the rotation time has elapsed, it should switch to forward motion
    advanceFakeMicros(700000);  // push total elapsed > rotateDuration
    basis.update();
    TEST_ASSERT_EQUAL(RollingBasis::Phase::Forwarding, basis.getPhaseForTest());
    TEST_ASSERT_TRUE(left.getTargetSpeedStepsPerSecForTest() >
                     0.0f);  // now both drive forward
    TEST_ASSERT_TRUE(right.getTargetSpeedStepsPerSecForTest() > 0.0f);
}

int main(int argc, char** argv) {
    UNITY_BEGIN();
    RUN_TEST(test_motor_scaling_and_enable);
    RUN_TEST(test_motor_acceleration_ramp_and_steps);
    RUN_TEST(test_point_distance_and_angle);
    RUN_TEST(test_rolling_basis_forward_motion);
    RUN_TEST(test_rolling_basis_rotation_then_forward);
    return UNITY_END();
}
