from multiprocessing import Manager


class DictProxyAccessor:
    """
    Class to access a DictProxy object as if it were a normal object.
    Avoid dict["key"] notation by using dict.key notation
    """

    def __init__(self) -> None:
        """
        Initialize the DictProxyAccessor by creating a DictProxy object
        """
        self._dict_proxy = Manager().dict()

    def __getattr__(self, key):
        """
        Intercept the call to an attribute of the object and redirect it to the DictProxy object
        :param key: key to access in the DictProxy
        :return: value of the key in the DictProxy
        """
        try:
            return self._dict_proxy[key]
        except Exception as e:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            ) from e

    def __setattr__(self, key, value) -> None:
        """
        Intercept the call to set an attribute of the object and redirect it to the DictProxy object.
        If the key is _dict_proxy, set the value in the object itself
        :param key:
        :return:
        """
        if key == "_dict_proxy":
            super().__setattr__(key, value)
        else:
            self._dict_proxy[key] = value

    def __delattr__(self, key) -> None:
        """
        Allow to delete an attribute of the object
        :param key:
        :return:
        """
        if key in self._dict_proxy:
            del self._dict_proxy[key]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def get_dict(self) -> dict:
        """
        Return the DictProxy object
        """
        return dict(self._dict_proxy.items())
