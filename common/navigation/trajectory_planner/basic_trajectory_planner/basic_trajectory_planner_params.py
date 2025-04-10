# ====== Code Summary ======
# This module defines a `BasicTrajectoryPlannerParams` class that extends the base parameter class
# `BaseTrajectoryPlannerParams`. It currently serves as a placeholder for future parameter extensions
# and calls the parent constructor.

# ====== Internal Project Imports ======
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import (
    BaseTrajectoryPlannerParams,
)
from navigation.trajectory_planner.structs import TrajectoryPlannerStrategy


class BasicTrajectoryPlannerParams(BaseTrajectoryPlannerParams):
    """
    Basic implementation of trajectory planner parameters.
    Inherits from BaseTrajectoryPlannerParams and can be extended with specific fields as needed.
    """

    def __init__(
        self, segment_length_threshold: float = 5.0, complexity_threshold: float = 2.0
    ) -> None:
        """
        Initialize basic trajectory planner parameters.
        Currently, this class does not introduce new parameters.

        Args:
            segment_length_threshold (float): Threshold for segment length.
            complexity_threshold (float): Threshold for complexity.
        """
        super().__init__(trajectory_planning_strategy=TrajectoryPlannerStrategy.BASIC)
        self.segment_length_threshold = segment_length_threshold
        # Chaque segment couvre environ 5 unités

        self.complexity_threshold = complexity_threshold
        # Un segment est ajouté pour chaque 0.5 radians de courbure
