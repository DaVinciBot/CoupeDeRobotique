# ====== Code Summary ======
# This module defines the BaseAvoidanceParams class, which encapsulates common configuration
# parameters shared across different obstacle avoidance strategies. It includes the selected
# avoidance strategy, the ACS (Automatic Collision System) trigger distance, and an optional
# timeout value for avoidance procedures.

# ====== Standard Library Imports ======
# (None)

# ====== Third-party Library Imports ======
# (None)

# ====== Internal Project Imports ======
from navigation.avoidance.structs import AvoidanceStrategy

# from navigation.avoidance.acs_detection_profile import BaseAcsDetectionProfile


class BaseAvoidanceParams:
    """
    Base class for defining common parameters used in avoidance strategies.

    This class serves as a container for configuration values such as the avoidance
    strategy type, the ACS detection distance, and a timeout duration.

    Attributes:
        avoidance_strategy (AvoidanceStrategy): Enum indicating the avoidance strategy.
        acs_distance (float): Distance threshold to trigger avoidance behavior.
        timeout (float): Maximum time to attempt avoidance before aborting (default is 0.0).
    """

    def __init__(
        self,
        avoidance_strategy: AvoidanceStrategy,
        # acs_detection_profile: BaseAcsDetectionProfile,
        acs_distance: float,
        timeout: float = 0.0,
    ):
        """
        Initialize the base avoidance parameters.

        Args:
            avoidance_strategy (AvoidanceStrategy): The selected avoidance strategy.
            acs_distance (float): Distance threshold for activating avoidance.
            timeout (float, optional): Timeout duration in seconds. Defaults to 0.0.
        """
        self.avoidance_strategy: AvoidanceStrategy = avoidance_strategy
        # self.acs_detection_profile: BaseAcsDetectionProfile = acs_detection_profile
        self.acs_distance: float = acs_distance
        self.timeout: float = timeout
