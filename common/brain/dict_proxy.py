from multiprocessing import Manager

from geometry import OrientedPoint, Point
from logger import Logger


class DictProxyAccessor:
    """
    Class to access a DictProxy object as if it were a normal object.
    Avoid dict["key"] notation by using dict.key notation
    """

    def __init__(self, name="Undefined name") -> None:
        """
        Initialize the DictProxyAccessor by creating a DictProxy object
        """
        self._dict_proxy = Manager().dict()
        self._name = name
        self._updated_attributes = set()

    def __getattr__(self, item):
        if item in ["_dict_proxy", "_name", "_updated_attributes"]:
            return object.__getattribute__(self, item)

        try:
            attr = object.__getattribute__(self, item)
            if callable(attr):
                return attr
        except AttributeError:
            pass  # Si l'attribut n'existe pas, on continue pour vérifier dans _dict_proxy

            # Tentative d'accès à un élément dans _dict_proxy si ce n'est pas une méthode
        try:
            return self._dict_proxy[item]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{item}'"
            )

    def __setattr__(self, key, value):
        if key in ["_dict_proxy", "_name", "_updated_attributes"]:
            object.__setattr__(self, key, value)
        else:
            self._dict_proxy[key] = value
            if key not in self._updated_attributes:
                self._updated_attributes.add(key)

    def get_updated_attributes(self):
        return self._updated_attributes

    def remove_updated_attribute(self, key):
        if key in self._updated_attributes:
            self._updated_attributes.remove(key)

    def get_dict(self) -> dict:
        """
        Return the DictProxy object
        """
        return dict(self._dict_proxy.items())

    def __str__(self):
        return self._name

    @staticmethod
    def is_serialized(obj) -> bool:
        # Tuple of all types that are considered serialized directly.
        serialized_types = (
            Logger,
            int,
            float,
            str,
            list,
            set,
            dict,
            tuple,
            OrientedPoint,
            Point,
            type(None),
        )

        if isinstance(obj, serialized_types):
            return True

        # Special case for an object with a __name__ attribute equal to "CONFIG".
        try:
            return obj.__name__ == "CONFIG"
        except AttributeError:  # If the object doesn't have the __name__ attribute.
            return False
