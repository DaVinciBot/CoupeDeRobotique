#include "actionneur_sweep.h"

#include "../../../include/config.h"

// SG-90: 50Hz, 0° = 500us, 180° = 2400us
// 14-bit resolution => 16384 ticks per 20ms (20000us)
// duty = pulseUs * 16384 / 20000
static const uint32_t SERVO_FREQ = 50;
static const uint8_t SERVO_RESOLUTION = 14;
static const uint16_t PULSE_MIN_US = 500;   // 0 degrees
static const uint16_t PULSE_MAX_US = 2400;  // 180 degrees

ActionneurSweep::ActionneurSweep(uint8_t pin, unsigned long durationMs)
    : _pin(pin), _durationMs(durationMs) {}

void ActionneurSweep::setServoAngle(uint8_t angle) {
    uint32_t pulseUs =
        PULSE_MIN_US + (uint32_t)(PULSE_MAX_US - PULSE_MIN_US) * angle / 180;
    uint32_t duty = pulseUs * 16384 / 20000;
    ledcWrite(0, duty);
}

void ActionneurSweep::start() {
    _started = true;
    _finished = false;

    ledcSetup(0, SERVO_FREQ, SERVO_RESOLUTION);
    ledcAttachPin(_pin, 0);

    DEBUG_PRINTF("[Sweep] Start on pin %u for %lu ms\n", _pin, _durationMs);

    unsigned long startMs = millis();

    while (millis() - startMs < _durationMs) {
        setServoAngle(180);
        delay(500);
        if (millis() - startMs >= _durationMs) break;

        setServoAngle(0);
        delay(500);
    }

    // Stop servo signal
    ledcWrite(0, 0);
    ledcDetachPin(_pin);
    _finished = true;
    DEBUG_PRINTLN("[Sweep] Finished");
}

void ActionneurSweep::update() {}

void ActionneurSweep::stop() {
    ledcWrite(0, 0);
    ledcDetachPin(_pin);
    _finished = true;
}

bool ActionneurSweep::isFinished() const {
    return _finished;
}

const char* ActionneurSweep::name() const {
    return "ActionneurSweep";
}
