# ====== Code Summary ======
# This module defines the NavigatorTask class, which orchestrates path planning, trajectory planning,
# and obstacle avoidance for autonomous navigation. Based on provided configuration parameters,
# it dynamically instantiates components like planners (Delta, Basic, Sequential) and the stop-and-wait
# avoidance strategy. It manages the navigation lifecycle through methods for planning, timeout handling,
# completion detection, and reactive avoidance execution.

# ====== Standard Library Imports ======
import time

# ====== Internal Project Imports ======
from arena import AllyZone, EnemyZone
from geometry import OrientedPoint

from navigation.trajectory_planner import (
    BaseTrajectoryPlanner,
    TrajectoryPlanCommand,
    TrajectoryPlannerFactory,
)

from navigation.path_planner import (
    BasePathPlanner,
    BasePathPlannerPlanPathParams,
    PathPlannerFactory,
    PathPlannerPathPlanParamsFactory,
)

from navigation.avoidance import (
    BaseAvoidance,
    AvoidanceFactory,
)

from navigation.navigator.task import NavigatorTaskParams
from navigation.navigator.task.states import NavigatorTaskState


class NavigatorTask:
    """
    A task responsible for executing autonomous navigation including path planning,
    trajectory generation, and obstacle avoidance.

    Attributes:
        params (NavigatorTaskParams): Configuration parameters for the task.
        path_planner (BasePathPlanner): The path planner instance.
        trajectory_planner (BaseTrajectoryPlanner): The trajectory planner instance.
        avoidance (BaseAvoidance): The obstacle avoidance handler.
        current_trajectory_command (TrajectoryPlanCommand | None): Currently active trajectory command.
        state (NavigatorTaskState): Current state of the task.
        _start_time (float): Internal timestamp when the task started.
    """

    def __init__(self, params: NavigatorTaskParams):
        """
        Initialize the NavigatorTask with the required parameters.

        Args:
            params (NavigatorTaskParams): Task configuration including planners and goals.
        """
        self.params: NavigatorTaskParams = params

        # Instantiate the components
        self.path_planner: BasePathPlanner = PathPlannerFactory.instantiate(
            params.path_planner_params,
        )
        self.trajectory_planner: BaseTrajectoryPlanner = (
            TrajectoryPlannerFactory.instantiate(
                params.trajectory_planner_params,
                params.speed_profiler,
            )
        )
        self.avoidance: BaseAvoidance = AvoidanceFactory.instantiate(
            params.avoidance_params,
        )

        self.current_trajectory_command: TrajectoryPlanCommand | None = None
        self.state: NavigatorTaskState = NavigatorTaskState.NOT_PLANNED
        self._start_time: float = 0.0

    def _get_elapsed_time(self) -> float:
        """
        Get the elapsed time since the task started.

        Returns:
            float: Time in seconds since the task was initiated.
        """
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def _plan_task(self, ally_zone: AllyZone) -> None:
        """
        Plan the path and trajectory based on the current position and task goal.

        Args:
            ally_zone (AllyZone): Current position of the ally used for planning.
        """
        # Start the timer
        self._start_time = time.time()

        # Generate path planning parameters from current state
        plan_path_params: BasePathPlannerPlanPathParams = (
            PathPlannerPathPlanParamsFactory.instantiate(
                strategy=self.params.path_planner_params.path_finding_strategy,
                current_position=ally_zone.point,
                goal=self.params.goal,
            )
        )

        # Plan the path using the appropriate strategy
        path: list[OrientedPoint] = self.path_planner.plan_path(plan_path_params)
        
        print("############ PATH PLANNED:", path)

        # Generate a trajectory based on the path
        self.trajectory_planner.plan_trajectory(path)

        # Mark task as in progress
        self.state = NavigatorTaskState.IN_PROGRESS

    def _has_timed_out(self) -> bool:
        """
        Check if the task has exceeded its time limit.

        Returns:
            bool: True if the timeout has been exceeded.
        """
        # Timeout is not set
        if self.params.timeout is None or self._start_time is None:
            return False
        # Timeout is set
        return self._get_elapsed_time() > self.params.timeout

    def _abort(self) -> TrajectoryPlanCommand:
        """
        Abort the task and issue a stop command.

        Returns:
            TrajectoryPlanCommand: Command to halt navigation.
        """
        self.state = NavigatorTaskState.ABORT
        self.current_trajectory_command = TrajectoryPlanCommand.create_stop_command(
            current_position=self.params.goal
        )
        return self.current_trajectory_command

    def _is_finished(self) -> bool:
        """
        Check if the trajectory has been completed.

        Returns:
            bool: True if task duration has exceeded total planned trajectory duration.
        """
        # If the task is not started or already finished, return False
        if self._start_time is None or self.state == NavigatorTaskState.FINISHED:
            return False
        return self._get_elapsed_time() > self.trajectory_planner.get_total_duration()

    def handle(
        self, ally_zone: AllyZone, enemy_zone: EnemyZone
    ) -> TrajectoryPlanCommand:
        """
        Manage the task lifecycle: planning, timeout checks, completion, and avoidance.

        Args:
            ally_zone (AllyZone): Current position of the ally.
            enemy_zone (EnemyZone): Position of enemy (for avoidance).

        Returns:
            TrajectoryPlanCommand: The current or updated trajectory plan command.
        """
        # 1. Plan if not already done
        if self.state == NavigatorTaskState.NOT_PLANNED:
            self._plan_task(ally_zone)

        # 2. Timeout check
        if self._has_timed_out():
            return self._abort()

        # 3. Completion check
        if self._is_finished():
            self.state = NavigatorTaskState.FINISHED

        # 4. Obstacle avoidance
        avoidance_cmd = self.avoidance.handle(
            current_navigator_task=self,
            ally_zone=ally_zone,
            enemy_zone=enemy_zone,
        )
        if self.state == NavigatorTaskState.AVOIDING:
            return avoidance_cmd

        # 5. Continue with planned trajectory
        self.current_trajectory_command = self.trajectory_planner.get_plan()
        return self.current_trajectory_command
