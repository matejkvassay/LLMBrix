class GraphState:
    """
    Object used by NodeBase instances during Graph execution.
    Serves to either read or write inputs and outputs from NodeBase execution.
    """

    def __init__(self, data: dict = None):
        super().__setattr__("_data", data or {})
        super().__setattr__("_protected_attrs", frozenset(self.__dict__.keys()))

    def write(self, **kwargs):
        """
        Write kwargs to internal storage.

        :param kwargs: Keys are used as keys in internal storage, values as values to be stored.
        """
        self._data.update(kwargs)

    def read(self, key):
        """
        Read value under a key in the internal storage.

        :param key: Key to read value from. If key not found KeyError is raised.
        :return: Value stored under the key.
        """
        try:
            return self._data[key]
        except KeyError as e:
            raise KeyError(f"GraphState no value stored under key: '{key}'") from e

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __getitem__(self, item):
        return self.read(item)

    def __setitem__(self, key, value):
        self.write(**{key: value})

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"GraphState has no attribute or key '{name}'")

    def __setattr__(self, name, value):
        if name in self._protected_attrs:
            super().__setattr__(name, value)
        else:
            self.write(**{name: value})

    def __repr__(self):
        if not self._data:
            return "GraphState(empty)"
        lines = "\n".join(f"  {k!r}: {v!r}," for k, v in self._data.items())
        return f"GraphState{{\n{lines}\n}}"
