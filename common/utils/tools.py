from geometry import OrientedPoint


def objectToStr(objet):
    if not hasattr(objet, "__dict__"):
        return "L'objet fourni n'est pas une instance de classe."
    str = ""
    for nom_parametre, valeur_parametre in objet.__dict__.items():
        if callable(valeur_parametre):
            str += f"{nom_parametre}: {valeur_parametre.__name__} ,"
        else:
            str += f"{nom_parametre}: {valeur_parametre} ,"
    str += "\n"
    return str
