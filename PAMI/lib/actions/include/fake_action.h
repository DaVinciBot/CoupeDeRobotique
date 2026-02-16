#ifndef ACTIONS_FAKE_ACTION_H
#define ACTIONS_FAKE_ACTION_H

#include "action.h"
#include "rolling_basis.h"

class FakeAction : public Action {
   public:
    FakeAction(RollingBasis* rb);
    ~FakeAction() = default;

    void start() override;
    void update() override;
    void stop() override;
    bool isFinished() const override;
    const char* name() const override;

   private:
    RollingBasis* _rb;
};

#endif
