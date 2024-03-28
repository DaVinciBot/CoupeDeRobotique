'''
class DictProxyAccessor:
    """
    Class to access a DictProxy object as if it were a normal object.
    Avoid dict["key"] notation by using dict.key notation
    """

    def __init__(self, name="Undefined name") -> None:
        """
        Initialize the DictProxyAccessor by creating a DictProxy object
        """
        from multiprocessing import Manager
        self._dict_proxy = Manager().dict()
        self._name = name
        self._updated_attributes = set()

    def __getattr__(self, key):
        """
        Intercept the call to an attribute of the object and redirect it to the DictProxy object
        :param key: key to access in the DictProxy
        :return: value of the key in the DictProxy
        """
        try:
            # Try to get the attribute from the object itself
            return super().__getattribute__(key)
        except AttributeError:
            # If it fails, try to get it from the DictProxy
            try:
                return self._dict_proxy[key]
            except KeyError:
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{key}'"
                ) from None

    def __setattr__(self, key, value) -> None:
        """
        Intercept the call to set an attribute of the object and redirect it to the DictProxy object.
        If the key is _dict_proxy, set the value in the object itself
        """
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self._dict_proxy[key] = value
            self._updated_attributes.add(key)

    def __delattr__(self, key) -> None:
        """
        Allow to delete an attribute of the object
        """
        if key.startswith('_'):
            super().__delattr__(key)
        elif key in self._dict_proxy:
            del self._dict_proxy[key]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def get_dict(self) -> dict:
        """
        Return the DictProxy object
        """
        return dict(self._dict_proxy.items())

    def get_updated_attributes(self):
        return self._updated_attributes

    def remove_updated_attribute(self, key):
        if key in self._updated_attributes:
            self._updated_attributes.remove(key)

    def __str__(self):
        return self._name

'''

from multiprocessing import Manager


class DictProxyAccessor:
    def __init__(self, name="undefined_name"):
        self._dict_proxy = Manager().dict()
        self._name = name
        self._updated_attributes = set()

    def __getattr__(self, key):
        try:
            if key in self.__dict__:
                return self.__dict__[key]
            elif key in self._dict_proxy:
                return self._dict_proxy[key]
        except Exception as error:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}' [{error}]")

    def __setattr__(self, key, value):
        if key in self.__dict__ or key in ['_dict_proxy', '_name', '_updated_attributes']:
            super().__setattr__(key, value)
        else:
            self._dict_proxy[key] = value

    def get_updated_attributes(self):
        return self._updated_attributes

    def remove_updated_attribute(self, key):
        if key in self._updated_attributes:
            self._updated_attributes.remove(key)

    def get_dict(self) -> dict:
        return dict(self._dict_proxy.items())

    def __str__(self):
        return self._name
