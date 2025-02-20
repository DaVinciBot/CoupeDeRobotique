from geometry import OrientedPoint
from movement.trajectory_computer.trajectory_params import TrajectoryParams
from arena import BaseArena, GridManager, BaseArenaZone
from path_finding import PathFinder

from geometry import Point, Polygon

from loggerplusplus import Logger


class TrajectoryComputer:
    def __init__(
            self,
            # Loggers:
            logger: Logger,
            path_finder_logger: Logger,
            # Arena (should be a pointer of the arena)
            arena_ptr: BaseArena,
            # Trajectory params
            trajectory_params: TrajectoryParams,
    ):
        self.logger: Logger = logger
        self.path_finder_logger: Logger = path_finder_logger

        self.arena_ptr: BaseArena = arena_ptr
        self.trajectory_params = trajectory_params

        self.path_finder: PathFinder | None = None

    def _get_goal(self) -> OrientedPoint | Point:
        # Get goal with OrientedPoint format

        # If goal is a BaseArenaZone
        if isinstance(self.trajectory_params.goal, BaseArenaZone):
            # Use zone method to get best goal point from zone
            goal = self.trajectory_params.goal.get_go_to_position(
                ally_position=self.arena_ptr.ally_zone.point, team_color=self.arena_ptr.team_color
            )

            # If goal is None => zone is not accessible
            if goal is None:
                self.logger.error("Goal is not accessible.")
                return

            # If goal is not an OrientedPoint ça veut dire que acune go to position n'est définie
            # On calcule alors automatiquemnt ce point
            if not isinstance(goal, OrientedPoint):
                goal = self._compute_go_to_destination_from_zone()

            # TODO: prendre en compte que quand on a que un point en goal, on ne peut pas avoir de theta,
            #  il faut le cacluler automatiqument (le même que celui d'avant dans la trjectoire par exmepl) voir pour mettre ay niveay du pathfinder

            return goal

    def _compute_go_to_destination_from_zone(self) -> Point:
        # Get goal zone centroid
        centroid = self.trajectory_params.goal.centroid
        new_x = centroid.x
        new_y = centroid.y

        # Check if the goal is too close to the border
        if centroid.x < self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer:
            new_x = self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer
        if (self.arena_ptr.width - centroid.x) < (
                self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer
        ):
            new_x = self.arena_ptr.width - (self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer)
        if centroid.y < self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer:
            new_y = self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer
        if (self.arena_ptr.height - centroid.y) < (
                self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer
        ):
            new_y = self.arena_ptr.height - (self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer)

        return Point(new_x, new_y)

    def _init_path_finder(self):
        self.path_finder = PathFinder(
            logger=self.path_finder_logger,
            start=self.arena_ptr.ally_zone.point,
            goal=self._get_goal(),
            grid_manager=self.arena_ptr.grid_manager,
            path_resolution=self.trajectory_params.resolution,
        )

    def compute(
            self,
            use_static_and_dynamic_grid: bool,
            current_position: OrientedPoint = None,
            current_linear_speed: float = None,
            current_angular_speed: float = None,
    ):
        self.compute_path(use_static_and_dynamic_grid, current_position)

    def compute_path(
            self,
            use_static_and_dynamic_grid: bool,
            current_position: OrientedPoint = None,
    ) -> list[OrientedPoint]:
        # Initie pathfinder if not aready done
        if self.path_finder is None:
            self._init_path_finder()
        else:
            # Update pathfinder with current position
            self.path_finder.update_current_position(
                self.arena_ptr.ally_zone.point if current_position is None else current_position
            )

        # Run pathfinder
        self.path_finder.find_oriented_path(
            use_static_and_dynamic_grid=use_static_and_dynamic_grid,
            smooth_path=self.trajectory_params.smooth_trajectory
        )

        return self.path_finder.oriented_path_found
