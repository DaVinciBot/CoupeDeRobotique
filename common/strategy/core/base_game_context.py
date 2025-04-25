from arena import BaseArena


class BaseGameContext:
    def __init__(self, arena: BaseArena) -> None:
        self.arena: BaseArena = arena
