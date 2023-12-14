import time
from classes import constants
# use lidarTools.py in order to develop functions using the lidar. In enables to test and use those one without having access to it


def get_current_date():
    from datetime import datetime
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    return {
        "date": now,
        "date_timespamp": timestamp
    }

def is_list_of(list : list, type)->bool:
    """tell wether the list contains only element of the given type

    Args:
        list (list): the list to test
        type (_type_): an object with requiered type

    Returns:
        bool: true if all the elements of list are elements of the given type
    """
    test = True
    n = 0
    while test and n<list.count():
        if not isinstance(list[n],type(type)):
            test = False
        n+=1
    return test
    
def is_in_tab(tableau, valeur):
    # Fonction auxiliaire pour effectuer la recherche
    def is_in(tableau, debut, fin, valeur):
        # Cas de base: tableau vide
        if debut > fin:
            return False

        # Calculer l'indice du milieu
        milieu = (debut + fin) // 2

        # Vérifier si la valeur est au milieu+
        if tableau[milieu] == valeur:
            return True
        # Si la valeur est inférieure, recherche à gauche
        elif tableau[milieu] > valeur:
            return is_in(tableau, debut, milieu - 1, valeur)
        # Sinon, recherche à droite
        else:
            return is_in(tableau, milieu + 1, fin, valeur)

    # Appel initial avec l'ensemble du tableau
    return is_in(tableau, 0, len(tableau) - 1, valeur)

def get_polar_points(self):
    return self.__scan_values_to_polar()