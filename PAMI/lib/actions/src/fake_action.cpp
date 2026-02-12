#include "fake_action.h"

FakeAction::FakeAction(RollingBasis* rb) : _rb(rb) {}

void FakeAction::start() {
    Serial.println("FakeAction started");
}

void FakeAction::update() {
    Serial.println("FakeAction updating...");
}

void FakeAction::stop() {
    Serial.println("FakeAction stopped");
}

bool FakeAction::isFinished() const {
    return false;
}

const char* FakeAction::name() const {
    return "FakeAction";
}
