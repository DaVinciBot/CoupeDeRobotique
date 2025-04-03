# ====== Code Summary ======
# This module defines a base class `BaseTrajectoryPlannerParams` intended to serve as a base for
# planner parameter configurations. The base implementation includes a no-op constructor.

class BaseTrajectoryPlannerParams:
    """
    Base class for trajectory planner parameter configurations.
    Can be extended by specific planner parameter classes to include additional settings.
    """

    def __init__(self) -> None:
        """
        Initialize the base planner parameters.
        Currently, this base class has no attributes or logic.
        """
        return
