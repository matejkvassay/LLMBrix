import uuid
from typing import Callable


class State:
    def __init__(self):
        self.data = dict()

    def __getitem__(self, item):
        return self.read(item)

    def write(self, **kwargs):
        self.data.update(kwargs)

    def read(self, key):
        return self.data[key]


class Node:
    def __init__(self, func: Callable[[State], None], name: str = None):
        self.uid = uuid.uuid4().int
        self.name = name or func.__qualname__
        self.func = func

    def run(self, state: State):
        self.func(state)

    def __hash__(self):
        return hash(self.uid)

    def __str__(self):
        return f"{self.name}_{self.uid}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Node) and self.uid == other.uid


class RouterNode:
    def __init__(self, state_key: str, node_map: dict[str, Node], name: str = None):
        self.uid = uuid.uuid4().int
        self.name = name or f"router_{state_key}"
        self.state_key = state_key
        self.node_map = node_map

    def run(self, state: State) -> Node:
        value = state.read(self.state_key)
        return self.node_map[value]

    def __hash__(self):
        return hash(self.uid)

    def __str__(self):
        return f"{self.name}_{self.uid}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, RouterNode) and self.uid == other.uid


class Graph:
    def __init__(self, start_node: Node | RouterNode, edges: list[tuple[Node | RouterNode, Node | RouterNode]]):
        self.start_node = start_node
        self.successors = {u: v for (u, v) in edges}

    def run(self, state: State):
        node = self.start_node
        while node:
            if isinstance(node, Node):
                node.run(state)
                if node in self.successors:
                    node = self.successors[node]
                else:
                    break
            elif isinstance(node, RouterNode):
                node = node.run(state)
            else:
                raise TypeError(f"Unrecognized graph node type: {type(node)}")
