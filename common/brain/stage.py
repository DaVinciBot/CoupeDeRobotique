class Stage:
    def __init__(self, func: function, identifient, stime, etime) -> None:
        """a stage contain a function, the time it needs to be executed and the time it must be aborted

        Args:
            func (function): the timed function to execute
            identifient (_type_): an id
            stime (_type_): launching time
            etime (int, optional): ending time.
        """
        self.func = func
        self.identifient = identifient
        self.stime = stime  # starting time
        if etime < 0:
            self.etime = etime  # default ending_time
        else:
            self.etime = -1
