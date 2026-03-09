#include <Arduino.h>
#include "AtoB.h"
#include "carre.h"
#include "config.h"
#include "motor.h"
#include "relative_forward.h"
#include "relative_turning.h"
#include "rolling_basis.h"
#include "strategy.h"
#include "triangle.h"

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

RollingBasis* rb = new RollingBasis(leftMotor,
                                    rightMotor,
                                    WHEEL_DIAMETER_MM,
                                    WHEEL_BASE_MM,
                                    Point{0, 0, 0});

Strategy* strategy = new Strategy(rb);

void setup() {
    Serial.begin(115200);

    strategy->addAction(new Carre(rb, 200, 0));
    strategy->addAction(new Triangle(rb, 150, 0));
    strategy->addAction(new RelativeForward(rb, 100));
    strategy->addAction(new RelativeTurning(rb, M_PI / 2));
    strategy->addAction(new AtoB(rb, Point{0, 0, 0}));

    strategy->start();
}

void loop() {
    if (!strategy->isFinished()) {
        strategy->update();
    }
}