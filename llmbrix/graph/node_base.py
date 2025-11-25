from abc import ABC, abstractmethod

from llmbrix.graph.graph_state import GraphState


class NodeBase(ABC):
    """
    Executable node of Graph.
    """

    def __init__(self, uid: int, name: str):
        """
        :param uid: int unique identifier
        :param name: str readable name of node
        """
        self.uid = uid
        self.name = name

    @abstractmethod
    def run(self, state: GraphState) -> "NodeBase | None":
        """
        Perform the node action.

        :param state: GraphState - used to read inputs and write outputs.
        :return: Regular Nodes return None, RouterNodes return NodeBase.
        """

    def __hash__(self):
        return hash(self.uid)

    def __str__(self):
        return f"{self.name}_{self.uid}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return type(self) is type(other) and self.uid == other.uid
