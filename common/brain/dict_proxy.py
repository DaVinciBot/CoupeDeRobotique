# ====== Standard Library Imports ======
from multiprocessing import Manager
from typing import Any

# ====== Internal Project Imports ======
from logger import Logger


# ====== Class Part ======
class DictProxyAccessor:
    """
    Class to access a DictProxy object as if it were a normal object.
    Avoid dict["key"] notation by using dict.key notation

    Attributes:
        _dict_proxy (Manager.dict): The dictionary proxy object being wrapped.
        _name (str): The name of the object.
        _updated_attributes (Set[str]): A set of attributes that have been updated.
    """

    def __init__(self, name: str = "Undefined name") -> None:
        """
        Initialize the DictProxyAccessor by creating a DictProxy object.

        Args:
            name (str): The name of the object. Defaults to "Undefined name".
        """
        self._dict_proxy: Manager.dict = Manager().dict()
        self._name: str = name
        self._updated_attributes: set[str] = set()

    def __getattr__(self, item: str) -> Any:
        """
        Get an attribute or a key from the DictProxy object.

        Args:
            item (str): The name of the attribute or key to access.

        Returns:
            Any: The value of the attribute or key.

        Raises:
            AttributeError: If the attribute or key does not exist.
        """
        if item in ["_dict_proxy", "_name", "_updated_attributes"]:
            return object.__getattribute__(self, item)

        try:
            attr: Any = object.__getattribute__(self, item)
            if callable(attr):
                return attr
        except AttributeError:
            pass  # If the attribute does not exist, continue to check in _dict_proxy

            # Attempt to access an item in _dict_proxy if it is not a method
        try:
            return self._dict_proxy[item]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{item}'"
            )

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Set an attribute or a key in the DictProxy object.

        Args:
            key (str): The name of the attribute or key.
            value (Any): The value to set.
        """
        if key in ["_dict_proxy", "_name", "_updated_attributes"]:
            object.__setattr__(self, key, value)
        else:
            self._dict_proxy[key] = value
            if key not in self._updated_attributes:
                self._updated_attributes.add(key)

    def get_updated_attributes(self) -> set[str]:
        """
        Get the set of attributes that have been updated.

        Returns:
            Set[str]: The set of updated attribute names.
        """
        return self._updated_attributes

    def remove_updated_attribute(self, key: str) -> None:
        """
        Remove an attribute from the updated attributes set.

        Args:
            key (str): The name of the attribute to remove.
        """
        if key in self._updated_attributes:
            self._updated_attributes.remove(key)

    def get_dict(self) -> dict:
        """
        Return the underlying DictProxy object as a regular dictionary.

        Returns:
            dict: The dictionary representation of the DictProxy object.
        """
        return dict(self._dict_proxy.items())

    def __str__(self) -> str:
        """
        Return the string representation of the object.

        Returns:
            str: The name of the object.
        """
        return self._name

    def __repr__(self) -> str:
        """
        Return the official string representation of the object.

        Returns:
            str: The name of the object.
        """
        return self.__str__()

    @staticmethod
    def is_serialized(obj: Any) -> bool:
        """
        Check if an object is of a type that is considered serialized directly.

        Args:
            obj (Any): The object to check.

        Returns:
            bool: True if the object is serialized, False otherwise.
        """
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
            type(None),
        )

        if isinstance(obj, serialized_types):
            return True

        # Special case for an object with a __name__ attribute equal to "CONFIG".
        try:
            return obj.__name__ == "CONFIG"
        except AttributeError:  # If the object doesn't have the __name__ attribute.
            return False
