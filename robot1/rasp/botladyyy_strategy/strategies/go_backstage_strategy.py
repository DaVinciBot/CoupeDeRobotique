"""Strategy that only deploys the banner before finishing."""

from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING

from botladyyy_strategy.strategies.base_strategy import BaseStrategy
from botladyyy_strategy.tasks.navigation_tasks.maneuver import (
    RelativeBackward,
    RelativeForward,
    RelativeRotation,
)
from botladyyy_strategy.tasks.navigation_tasks.odometrie import SetOdometrie
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.tasks import BaseTask

if TYPE_CHECKING:
    from botladyyy_strategy.winter_game_context import WinterGameContext

POSITION_TOLERANCE_CM = 0.9
ANGLE_TOLERANCE_RAD = 0.05
FINISH_AFTER_EXPECTED_END_DELAY_S = 5.0
END_START_DELAY_S = 90.0


class _StrategyTimer:
    """Shared monotonic timer for this strategy instance."""

    def __init__(self) -> None:
        self.start_time_s: float | None = None


class _MarkStrategyStart(BaseTask["WinterGameContext"]):
    """Record the actual strategy start time."""

    def __init__(self, timer: _StrategyTimer) -> None:
        """Initialize the start marker task.

        Args:
            timer (_StrategyTimer): Shared strategy timer to initialize.
        """
        super().__init__(estimated_duration=0.0, points=0)
        self._timer = timer

    def handle(self, _ctx: WinterGameContext) -> bool:
        if self._timer.start_time_s is None:
            self._timer.start_time_s = time.monotonic()
        return True


class _WaitUntilStrategyElapsed(BaseTask["WinterGameContext"]):
    """Wait until the strategy has been running for the requested duration."""

    def __init__(self, timer: _StrategyTimer, duration_s: float) -> None:
        """Initialize the wait task.

        Args:
            timer (_StrategyTimer): Shared strategy timer to read.
            duration_s (float): Required elapsed strategy duration in seconds.
        """
        super().__init__(estimated_duration=duration_s, points=0)
        self._timer = timer
        self._duration_s = duration_s

    def handle(self, _ctx: WinterGameContext) -> bool:
        if self._timer.start_time_s is None:
            self._timer.start_time_s = time.monotonic()

        return time.monotonic() - self._timer.start_time_s >= self._duration_s


class GoBackstageStrategy(BaseStrategy):
    """Deploy the banner then move directly to the backstage zone."""

    def __init__(self, ctx: WinterGameContext, rotation_sign: float = 1.0) -> None:
        """Initialize the strategy.

        Build the task flow using subgraphs and direct transitions.

        Args:
            ctx (WinterGameContext):
                Game context containing game-specific configurations and zones.
            rotation_sign (float):
                Direction multiplier for relative rotations.
        """
        super().__init__(ctx)

        strategy_timer = _StrategyTimer()

        def make_forward(name: str, distance: float) -> BaseTaskNode:
            return BaseTaskNode(
                name=name,
                tasks=RelativeForward(
                    distance=distance,
                    position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                    angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
                    finish_after_expected_end_delay_s=(
                        FINISH_AFTER_EXPECTED_END_DELAY_S
                    ),
                ),
            )

        def make_backward(name: str, distance: float) -> BaseTaskNode:
            return BaseTaskNode(
                name=name,
                tasks=RelativeBackward(
                    distance=distance,
                    position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                    angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
                    finish_after_expected_end_delay_s=(
                        FINISH_AFTER_EXPECTED_END_DELAY_S
                    ),
                ),
            )

        def make_turn(name: str, angle: float) -> BaseTaskNode:
            return BaseTaskNode(
                name=name,
                tasks=RelativeRotation(
                    angle=rotation_sign * angle,
                    position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                    angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
                    finish_after_expected_end_delay_s=(
                        FINISH_AFTER_EXPECTED_END_DELAY_S
                    ),
                ),
            )

        forward = BaseTaskNode(
            name="Move Forward",
            tasks=[
                _MarkStrategyStart(strategy_timer),
                RelativeForward(
                    distance=93.0,
                    position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                    angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
                    finish_after_expected_end_delay_s=FINISH_AFTER_EXPECTED_END_DELAY_S,
                ),
            ],
        )

        backward_20 = make_backward("Backward 20 cm", 24.0)
        turn_90_1 = make_turn("Turn 90 deg 1", math.pi / 2)
        forward_52 = make_forward("Forward 52 cm", 35.0)
        turn_minus_90_1 = make_turn("Turn -90 deg 1", -math.pi / 2)
        forward_90 = make_forward("Forward 96 cm", 110.0)
        reset_position = BaseTaskNode(
            name="Reset Position", tasks=SetOdometrie(0, 0, 0)
        )
        backward_20_2 = make_backward("Backward 20 cm", 8.5)
        turn_90_2 = make_turn("Turn 90 deg 2", math.pi / 2)
        forward_58_3 = make_forward("Forward 58.3 cm", 63.0)
        backward_22 = make_backward("Backward 22 cm", 85.0)
        turn_90_3 = make_turn("Turn 90 deg 3", math.pi / 2)
        forward_55 = make_forward("Forward 55 cm", 55.0)
        turn_90_4 = make_turn("Turn 90 deg 3", 0.14)
        forward_100 = make_forward("Forward 100 cm", 100.0)

        wait_before_end = BaseTaskNode(
            name="Wait Before End",
            tasks=_WaitUntilStrategyElapsed(strategy_timer, END_START_DELAY_S),
        )

        # Connect the subgraphs in execution order
        self._auto_build_transitions(
            forward,
            backward_20,
            turn_90_1,
            forward_52,
            turn_minus_90_1,
            forward_90,
            reset_position,
            backward_20_2,
            turn_90_2,
            forward_58_3,
            backward_22,
            turn_90_3,
            forward_55,
            turn_90_4,
            wait_before_end,
            forward_100,
        )

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=Logger(
                identifier="GoBackstageStrategy",
                follow_logger_manager_rules=True,
            ),
            start=forward,
        )
