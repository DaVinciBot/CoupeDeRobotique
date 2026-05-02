#ifndef STRATEGY_H
#define STRATEGY_H

#include <vector>

#include "AtoB.h"
#include "action.h"
#include "rolling_basis.h"

class Strategy : public Action {
   public:
    explicit Strategy(RollingBasis* rb);
    ~Strategy() override;

    void addAction(Action* action);
    void clearActions();

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

    void updateCurrentAction();

    void creer_strategie(const std::vector<Point>& points);
    void ajoute_strategie(const Point& point);
    void strategie_update();
    void setPointTrajectory(const std::vector<Point>& points);

   private:
    RollingBasis* _rb;
    std::vector<Action*> _actions;
    size_t _currentActionIndex = 0;
    bool _started = false;
    bool _finished = false;
    bool _stopped = false;

    void startCurrentAction();
};

#endif
