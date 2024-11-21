from brain.execution_states import ExecutionStates


class TaskOutput:
    def __init__(self, result, execution_state: ExecutionStates) -> None:
        self.result = result
        self.execution_state = execution_state

    def have_crashed(self) -> bool:
        return self.result == ExecutionStates.ERROR_OCCURRED

    def have_timeout(self) -> bool:
        return self.result == ExecutionStates.TIMEOUT

    def is_success(self) -> bool:
        return not self.have_timeout() and not self.have_crashed()