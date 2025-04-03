# ====== Code Summary ======
# This module defines a `BasicTrajectoryPlannerParams` class that extends the base parameter class
# `BaseTrajectoryPlannerParams`. It currently serves as a placeholder for future parameter extensions
# and calls the parent constructor.

# ====== Internal Project Imports ======
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import \
    BaseTrajectoryPlannerParams


class BasicTrajectoryPlannerParams(BaseTrajectoryPlannerParams):
    """
    Basic implementation of trajectory planner parameters.
    Inherits from BaseTrajectoryPlannerParams and can be extended with specific fields as needed.
    """

    def __init__(self) -> None:
        """
        Initialize basic trajectory planner parameters.
        Currently, this class does not introduce new parameters.
        """
        super().__init__()
