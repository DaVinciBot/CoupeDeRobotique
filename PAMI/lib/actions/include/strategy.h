#ifndef STRATEGY_H
#define STRATEGY_H
#include <vector>
#include "AtoB.h"
#include "action.h"
#include "actionneur.h"
#include "carre.h"
#include "relative_forward.h"
#include "relative_turning.h"
#include "rolling_basis.h"
#include "triangle.h"

class Strategy : public Action {
   public:
    Strategy(RollingBasis* rb);
    ~Strategy() = default;
    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;
    void updateCurrentAction();
    
    // Nouvelles fonctions pour gérer la stratégie simplement
    void creer_strategie(const std::vector<Point>& points);  // Initialise avec une liste de points
    void ajoute_strategie(const Point& point);               // Ajoute un point à la stratégie
    void strategie_update();                                 // Update strategy + rolling basis movement
    
    // Ajouter une liste de points à traverser avec AtoB
    void setPointTrajectory(const std::vector<Point>& points);

   private:
    RollingBasis* _rb;
    std::vector<Action*> _actions;
    int _currentActionIndex = 0;
    unsigned long _transitionDelay = 0;  // Pour les délais entre actions
    bool _waitingBetweenActions = false;
    void initActions();
};
#endif
