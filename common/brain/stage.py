class Stage:
    def __init__(self, func: function, identifient, start_t, end_time) -> None:
        """a stage contain a function, the time it needs to be executed and the time it must be aborted

        Args:
            func (function): the timed function to execute
            identifient (_type_): an id
            stime (_type_): launching time
            etime (int, optional): ending time.
        """
        self.func = func
        self.identifient = identifient
        self.stime = start_t  # starting time
        if end_time < 0:
            self.etime = end_time  # default ending_time
        else:
            self.etime = -1
