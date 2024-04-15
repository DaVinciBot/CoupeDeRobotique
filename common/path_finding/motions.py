from path_finding.node import Node


class Motions:
    """
    The plan convention is as follows:
    x++ -> froward
    x-- -> backward

    y++ -> left
    y-- -> right
    """
    def __init__(
            self,
            forward: tuple[int, int],
            backward: tuple[int, int],
            left: tuple[int, int],
            right: tuple[int, int],
            forward_left: tuple[int, int],
            forward_right: tuple[int, int],
            backward_left: tuple[int, int],
            backward_right: tuple[int, int]
        ):
        self.forward = Motions._instantiate_node(forward)
        self.backward = Motions._instantiate_node(backward)
        self.left = Motions._instantiate_node(left)
        self.right = Motions._instantiate_node(right)
        self.forward_left = Motions._instantiate_node(forward_left)
        self.forward_right = Motions._instantiate_node(forward_right)
        self.backward_left = Motions._instantiate_node(backward_left)
        self.backward_right = Motions._instantiate_node(backward_right)

    @staticmethod
    def _compute_cost(motion: tuple[int, int]):
        return math.sqrt(motion[0] ** 2 + motion[1] ** 2)

    @staticmethod
    def _instantiate_node(motion: tuple[int, int]):
        return Node(motion[0], motion[1], Motions._compute_cost(motion))
