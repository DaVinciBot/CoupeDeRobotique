#include <Arduino.h>
#include "config.h"
#include "forward_action.h"
#include "motor.h"
#include "navigation.h"
#include "rolling_basis.h"
#include "rotate_action.h"
#include "test_strategy.h"

Motor* leftMotor = new Motor(LEFT_STEP_PIN,
                             LEFT_DIR_PIN,
                             LEFT_EN_PIN,
                             LEFT_STEPS_PER_REV,
                             PULSE_US,
                             true);
Motor* rightMotor = new Motor(RIGHT_STEP_PIN,
                              RIGHT_DIR_PIN,
                              RIGHT_EN_PIN,
                              RIGHT_STEPS_PER_REV,
                              PULSE_US,
                              false);

RollingBasis* rollingBasis = new RollingBasis(leftMotor,
                                              rightMotor,
                                              WHEEL_DIAMETER_MM,
                                              WHEEL_BASE_MM,
                                              Point{0, 0, 0});
Navigation* navigation = new Navigation(rollingBasis, 15000);

// Actions
ForwardAction* a1 = new ForwardAction(rollingBasis, 2.0f);
RotateAction* a2 = new RotateAction(rollingBasis, 1.0f);
ForwardAction* a3 = new ForwardAction(rollingBasis, 2.0f);
RotateAction* a4 = new RotateAction(rollingBasis, 1.0f);

Action* actions[] = {a1, a2, a3, a4};
TestStrategy* strategy = new TestStrategy(navigation, actions, 4);

void setup() {
    Serial.begin(115200);
    strategy->start();
}

void loop() {
    if (!strategy->isFinished()) {
        strategy->update();
    }
}