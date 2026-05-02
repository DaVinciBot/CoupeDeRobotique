#include "strategy.h"

Strategy::Strategy(RollingBasis* rb) : _rb(rb) {}

Strategy::~Strategy() {
    clearActions();
}

void Strategy::addAction(Action* action) {
    if (action == nullptr) {
        Serial.println("[Strategy] Ignored null action");
        return;
    }

    _actions.push_back(action);
    _finished = false;

    Serial.printf("[Strategy] Action added: %s (total: %u)\n", action->name(),
                  static_cast<unsigned>(_actions.size()));
}

void Strategy::clearActions() {
    if (_started && !isFinished() && _currentActionIndex < _actions.size()) {
        _actions[_currentActionIndex]->stop();
    }

    for (Action* action : _actions) {
        delete action;
    }

    _actions.clear();
    _currentActionIndex = 0;
    _started = false;
    _finished = false;
    _stopped = false;
}

void Strategy::setPointTrajectory(const std::vector<Point>& points) {
    clearActions();

    for (const Point& point : points) {
        ajoute_strategie(point);
    }

    Serial.printf("[Strategy] Trajectory loaded with %u point(s)\n",
                  static_cast<unsigned>(_actions.size()));
}

void Strategy::creer_strategie(const std::vector<Point>& points) {
    setPointTrajectory(points);
}

void Strategy::ajoute_strategie(const Point& point) {
    addAction(new AtoB(_rb, point));
}

void Strategy::strategie_update() {
    update();
}

void Strategy::startCurrentAction() {
    if (_currentActionIndex >= _actions.size()) {
        _finished = true;
        return;
    }

    Action* currentAction = _actions[_currentActionIndex];
    Serial.printf("[Strategy] Starting action %u/%u: %s\n",
                  static_cast<unsigned>(_currentActionIndex + 1),
                  static_cast<unsigned>(_actions.size()),
                  currentAction->name());
    currentAction->start();
}

void Strategy::start() {
    _currentActionIndex = 0;
    _started = true;
    _finished = false;
    _stopped = false;

    if (_actions.empty()) {
        Serial.println("[Strategy] No action to run");
        _finished = true;
        return;
    }

    Serial.println("[Strategy] Started");
    startCurrentAction();
}

void Strategy::updateCurrentAction() {
    if (!_started || _finished || _stopped ||
        _currentActionIndex >= _actions.size()) {
        return;
    }

    _actions[_currentActionIndex]->update();
}

void Strategy::update() {
    if (!_started || _finished || _stopped) {
        return;
    }

    if (_currentActionIndex >= _actions.size()) {
        _finished = true;
        return;
    }

    Action* currentAction = _actions[_currentActionIndex];
    currentAction->update();

    if (!currentAction->isFinished()) {
        return;
    }

    Serial.printf("[Strategy] Finished action %u/%u: %s\n",
                  static_cast<unsigned>(_currentActionIndex + 1),
                  static_cast<unsigned>(_actions.size()),
                  currentAction->name());

    _currentActionIndex++;

    if (_currentActionIndex >= _actions.size()) {
        _finished = true;
        Serial.println("[Strategy] All actions finished");
        return;
    }

    startCurrentAction();
}

void Strategy::stop() {
    if (!_finished && _currentActionIndex < _actions.size()) {
        _actions[_currentActionIndex]->stop();
    }

    _stopped = true;
    _finished = true;
    Serial.println("[Strategy] Stopped");
}

bool Strategy::isFinished() const {
    return _finished || _stopped;
}

const char* Strategy::name() const {
    return "Strategy";
}
