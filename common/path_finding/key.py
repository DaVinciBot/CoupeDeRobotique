class Key:
    """
    Key class to represent the key value for a given vertex.
    It is a tuple of 2 values (k1, k2) where k1 is the priority and k2 is the secondary value.
    k1 -> primary key value
    k2 -> secondary key value (used to break ties)
    """
    def __init__(self, k1: tuple[float, float] | float, k2: float = 0.0):
        if isinstance(k1, tuple):
            self.k1 = k1[0]
            self.k2 = k1[1]
        else:
            self.k1 = k1
            self.k2 = k2

    def __lt__(self, other):
        """
        lexicographic 'lower than'
        :param other: comparable keys
        :return: lexicographic order
        """
        return self.k1 < other.k1 or (self.k1 == other.k1 and self.k2 < other.k2)

    def __le__(self, other):
        """
        lexicographic 'lower than or equal'
        :param other: comparable keys
        :return: lexicographic order
        """
        return self.k1 < other.k1 or (self.k1 == other.k1 and self.k2 <= other.k2)