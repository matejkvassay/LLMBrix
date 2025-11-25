class GraphState:
    """
    Object used by NodeBase instances during Graph execution.
    Serves to either read or write inputs and outputs from NodeBase execution.
    """

    def __init__(self, data=None):
        self.data = data or dict()

    def __getitem__(self, item):
        return self.read(item)

    def write(self, **kwargs):
        """
        :param kwargs: Keys are used as keys in internal storage, values as values to be stored.
        """
        self.data.update(kwargs)

    def read(self, key):
        """
        :param key: Key to read value from. If key not found KeyError is raised.
        :return: Value stored under the key.
        """
        try:
            return self.data[key]
        except KeyError as e:
            raise KeyError(f"GraphState no value stored under key: '{key}'") from e

    def __repr__(self):
        return f"GraphState(dict_keys={self.data.keys()})"
