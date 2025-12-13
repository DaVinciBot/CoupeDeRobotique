#include <unity.h>

#include "arduino_compat.h"
#include "motor.h"

void setUp() {
    resetFakeTime();
}
void tearDown() {}

void test_motor_scaling_and_enable() {
    Motor motor(1, 2, 3, 400, 500, false);
    motor.init();

    motor.setAcceleration(50.0f);
    motor.setTargetSpeed(300.0f);

    TEST_ASSERT_TRUE(motor.isMoving());
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 50.0f, motor.getAccelerationForTest());
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 300.0f,
                             motor.getTargetSpeedStepsPerSecForTest());
}

void test_motor_acceleration_ramp_and_steps() {
    Motor motor(4, 5, 6, 400, 500, false);
    motor.init();
    motor.setAcceleration(100.0f);
    motor.setTargetSpeed(40.0f);

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
    TEST_ASSERT_FLOAT_WITHIN(0.5f, 30.0f,
                             motor.getCurrentSpeedStepsPerSecForTest());

    advanceFakeMicros(200000);  // ramp a bit more and allow a step to occur
    motor.update();
    TEST_ASSERT_FLOAT_WITHIN(0.5f, 40.0f,
                             motor.getCurrentSpeedStepsPerSecForTest());

    motor.update();
    TEST_ASSERT_TRUE(motor.getStepCount() > 0);
}

int main(int argc, char** argv) {
    UNITY_BEGIN();
    RUN_TEST(test_motor_scaling_and_enable);
    RUN_TEST(test_motor_acceleration_ramp_and_steps);
    return UNITY_END();
}
