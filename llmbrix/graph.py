import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable


class GraphState:
    def __init__(self):
        self.data = dict()

    def __getitem__(self, item):
        return self.read(item)

    def write(self, **kwargs):
        self.data.update(kwargs)

    def read(self, key):
        try:
            return self.data[key]
        except KeyError as e:
            raise KeyError(f"GraphState no value stored under key: '{key}'") from e

    def __repr__(self):
        return f"GraphState(dict_keys={self.data.keys()})"


class NodeBase(ABC):
    def __init__(self, uid: int, name: str):
        self.uid = uid
        self.name = name

    @abstractmethod
    def run(self, state: GraphState) -> "NodeBase | None":
        """
        Perform the node action.
        Regular Nodes return None, RouterNodes return NodeBase.
        """

    def __hash__(self):
        return hash(self.uid)

    def __str__(self):
        return f"{self.name}_{self.uid}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return type(self) is type(other) and self.uid == other.uid


class Node(NodeBase):
    def __init__(self, func: Callable[[GraphState], None], name: str = None):
        uid = uuid.uuid4().int
        name = name or func.__qualname__
        super().__init__(uid=uid, name=name)
        self.func = func

    def run(self, state: GraphState):
        self.func(state)


class RouterNode(NodeBase):
    def __init__(self, state_key: str, node_map: dict[str, NodeBase], name: str = None):
        uid = uuid.uuid4().int
        name = name or f"router_{state_key}"
        super().__init__(uid=uid, name=name)
        self.state_key = state_key
        self.node_map = node_map
        for k, v in node_map.items():
            if not isinstance(v, NodeBase):
                raise ValueError(f"RouterNode node_map value for key {k} must be a NodeBase, got {type(v)}")

    def run(self, state: GraphState) -> NodeBase:
        value = state.read(self.state_key)
        if value not in self.node_map:
            raise ValueError(
                f'Value "{value}" not found in node map for router {self.name}. Available keys: {self.node_map.keys()}'
            )
        return self.node_map[value]


@dataclass
class GraphRunContext:
    node: NodeBase | None
    state: GraphState
    step: int
    finish_reason: str | None = None


class Graph:
    def __init__(
        self,
        start_node: NodeBase,
        edges: list[tuple[NodeBase, NodeBase]],
        middleware: Callable[[GraphRunContext], GraphRunContext] = None,
        step_limit: int = 100,
    ):
        self.start_node = start_node
        self.successors = {}
        for u, v in edges:
            if isinstance(u, RouterNode):
                raise ValueError(
                    f"RouterNode {u.name} cannot be used as edge source, " f"use node_map attribute on RouterNode."
                )
            if u in self.successors:
                raise ValueError(f"Multiple successors found for node {u}.")
            self.successors[u] = v
        self.middleware = middleware
        self.step_limit = step_limit

    def run(self, state: GraphState) -> GraphRunContext:
        context = GraphRunContext(node=self.start_node, state=state, step=0)
        while context.node:
            context.step += 1
            if context.step > self.step_limit:
                context.finish_reason = "step_limit"
                break
            if self.middleware:
                modified_context = self.middleware(context)
                if not isinstance(modified_context, GraphRunContext):
                    raise TypeError("Middleware must return GraphRunContext")
                if not isinstance(modified_context.node, (NodeBase, type(None))):
                    raise TypeError("Middleware returned invalid node")
                if not isinstance(modified_context.state, GraphState):
                    raise TypeError("Middleware returned invalid state")
                if (context.node is not None) and (modified_context.node is None):
                    if modified_context.finish_reason is None:
                        modified_context.finish_reason = "middleware"
                    context = modified_context
                    break
                context = modified_context
            node = context.node
            if node is None:
                context.finish_reason = "last_node"
                break
            elif isinstance(node, Node):
                node.run(context.state)
                if node in self.successors:
                    context.node = self.successors[node]
                else:
                    context.node = None
            elif isinstance(node, RouterNode):
                context.node = node.run(context.state)
            else:
                raise TypeError(f"Unrecognized graph node type: {type(node)}")
        return context
