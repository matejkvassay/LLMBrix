import uuid
from typing import Callable

from llmbrix.graph.graph_state import GraphState
from llmbrix.graph.node_base import NodeBase


def node(func=None, *, name: str = None):
    """
    Transforms function to Node object - make sure function takes GraphState as input.

    :param func: Callable, has to take 1 param - GraphState as input, output is ignored.
                     Should write results back into the GraphState.

    :param name: Optional, str human-readable name of this node.
                 If not provided its automatically taken from function/method name.
    :return: Node object.
    """

    def decorator(f):
        return Node(f, name=name)

    if callable(func):
        return decorator(func)
    return decorator


class Node(NodeBase):
    """
    Standard executable Node.
    Developer provides a function that reads/writes to state.
    This Node wraps the function so it's runnable in a LLM workflow Graph.
    """

    def __init__(self, func: Callable[[GraphState], None], name: str = None):
        """
        :param func: Callable, has to take 1 param - GraphState as input, output is ignored.
                     Should write results back into the GraphState.
        :param name: Optional, str human-readable name of this node.
                     If not provided its automatically taken from function/method name.
        """
        uid = uuid.uuid4().int
        name = name or func.__qualname__
        super().__init__(uid=uid, name=name)
        self.func = func

    def run(self, state: GraphState):
        """
        Execute this node (runs developer-provided function).

        :param state: GraphState object to read/write to, passed to developer-provided function
        """
        self.func(state)
