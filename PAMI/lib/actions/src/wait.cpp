#include "wait.h"

#include "../../../include/config.h"

Wait::Wait(unsigned long durationMs) : _durationMs(durationMs) {}

void Wait::start() {
    _finished = false;
    _startMs = millis();
    DEBUG_PRINTF("[Wait] %lu ms\n", _durationMs);
}

void Wait::update() {
    if (!_finished && millis() - _startMs >= _durationMs) {
        _finished = true;
        DEBUG_PRINTLN("[Wait] Done");
    }
}

void Wait::stop() {
    _finished = true;
}

bool Wait::isFinished() const {
    return _finished;
}

const char* Wait::name() const {
    return "Wait";
}
