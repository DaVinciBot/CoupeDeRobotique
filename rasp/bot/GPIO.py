import RPi.GPIO as IO

class PIN:
    """
    Classe permettant de gérer les pins GPIO de la rapberry pi
    """
    def __init__(self, pin: int, mode: str) -> None:
        """
        Initialise un pin GPIO

        :param pin: Numéro du pin ECRIT SUR LA CARTE
        :type pin: int
        :param mode: OUTPUT ou INPUT
        :type mode: str
        """
        self.pwm = False
        if pin in [33, 32]:
            self.pwm = True
        self.pin = pin
        if mode not in ["OUTPUT", "INPUT"]:
            raise Exception("Le mode doit être OUTPUT ou INPUT")
        self.mode = IO.OUT if mode == "OUTPUT" else IO.IN

        IO.setmode(IO.BOARD)
        IO.setup(self.pin, self.mode)

    def set(self, state: bool) -> None:
        """
        Modifie l'état du pin

        :param state: Etat du pin
        :type state: bool
        """
        if self.mode == IO.IN:
            raise Exception(
                "Le pin est en mode INPUT, il n'est pas possible de le modifier"
            )
        IO.output(self.pin, state)

    def get(self) -> bool:
        """
        Récupère l'état du pin

        :return: Etat du pin
        :rtype: bool
        """
        return IO.input(self.pin)

    def __del__(self) -> None:
        """
        Destructeur de la classe
        """
        IO.cleanup(self.pin)
        del self.pin
        del self.mode
