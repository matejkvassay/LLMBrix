from typing import Callable, Iterator

from graphviz import Digraph

from llmbrix.graph.graph_run_context import GraphRunContext
from llmbrix.graph.graph_state import GraphState
from llmbrix.graph.node import Node
from llmbrix.graph.node_base import NodeBase
from llmbrix.graph.router_node import RouterNode


class Graph:
    """
    Graph for LLM workflow consisting of interconnected NodeBase instances.

    Only simple Graphs are supported => no parallel branches, parallelism has to be handled within the Nodes.
    Router nodes can only select 1 successor at a time.
    """

    def __init__(
        self,
        start_node: NodeBase,
        steps: list[NodeBase | tuple[NodeBase, NodeBase]],
        middleware: Callable[[GraphRunContext], GraphRunContext] = None,
        step_limit: int = 100,
    ):
        """
        :param start_node: NodeBase to start execution with.
        :param steps: Nodes or edges specifying topography of the workflow Graph.
                      Allowed:
                        - Edge tuples (u, v), where u,v are NodeBase instances.
                        - Single dones u, where u is NodeBase Instance
                      Single nodes are expanded automatically to edge tuples, e.g.:
                                    [A, B, C] -> [(A, B), (B, C)]
                                    [A, (A, X), X, Y] -> [(A, X), (X, Y)]
                      Note u cannot be Router node (use node_map attribute for defining possible edges).
                      Only 1 successor per Node is allowed.
        :param middleware: Function that takes GraphRunContext at beginning of each iteration as input and outputs
                           modified GraphRunContext. Can be used to change GraphRunContext in real-time (e.g.
                           perform undo functionality or human-in-the-loop interruption).
                           Middleware runs at beginning of each iteration before the node in context is executed.
        :param step_limit: Safety limit - mandatory - this will limit number of steps (nodes visited) to break
                           infinite loops or hanged execution.
        """
        self.start_node = start_node
        self.successors = {}

        steps = self._expand_single_nodes_to_edges(steps)

        for u, v in steps:
            if not isinstance(u, NodeBase) or not isinstance(v, NodeBase):
                raise ValueError(f"Each edge node has to be instance of NodeBase. Got types {(type(u), type(v))}")
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
        """
        Runs Graph nodes.

        Algorithm overview:
            - initialize context
            - while loop:
                - yield context
                - check if step limit not reached
                - apply middleware if set
                - check if any node is selected for execution, if not terminate with "last_node" reason
                - if selected node is Node then execute and find successor
                - if selected node is RouterNode then execute to define successor
            - return final context

        :param state: Initial GraphState passed to start_node.
        :return: GraphRunContext after final execution step.
        """
        ctx = None
        for ctx in self.run_iter(state=state):
            pass
        return ctx

    def run_iter(self, state: GraphState) -> Iterator[GraphRunContext]:
        """
        Iteratively runs Graph nodes.

        Algorithm overview:
            - initialize context
            - while loop:
                - yield context
                - check if step limit not reached
                - apply middleware if set
                - check if any node is selected for execution, if not terminate with "last_node" reason
                - if selected node is Node then execute and find successor
                - if selected node is RouterNode then execute to define successor
            - yield final context
            - return

        :param state: Initial GraphState passed to start_node.
        :yield: GraphRunContext for each execution step.
        :return: Iterator over GraphRunContext updates during Graph execution.
        """
        context = GraphRunContext(node=self.start_node, state=state, step=0)
        while True:
            yield context
            if context.step >= self.step_limit:
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
            context.step += 1
        yield context

    def visualize(self, filename: str = "graph", view: bool = False, context: GraphRunContext | None = None) -> Digraph:
        dot = Digraph(comment="Graph")

        # Modern graph aesthetics
        dot.graph_attr.update(
            {
                "rankdir": "LR",  # left-to-right flow looks modern
                "splines": "spline",  # smooth curves
                "nodesep": "0.4",
                "ranksep": "0.6",
                "bgcolor": "white",
            }
        )
        dot.node_attr.update(
            {
                "shape": "box",
                "style": "filled,rounded",
                "fillcolor": "#f7f7f7",
                "color": "#cccccc",
                "fontname": "Helvetica",
                "fontsize": "10",
            }
        )
        dot.edge_attr.update(
            {
                "color": "#999999",
                "arrowhead": "vee",
                "arrowsize": "0.8",
                "fontname": "Helvetica",
                "fontsize": "9",
            }
        )

        # collect nodes
        all_nodes: set[NodeBase] = set(self.successors.keys())
        all_nodes.update(self.successors.values())
        for node in list(all_nodes):
            if isinstance(node, RouterNode):
                all_nodes.update(node.node_map.values())

        # add nodes
        for node in all_nodes:
            attrs = {}

            # Highlight current node
            if context is not None and context.node == node:
                attrs["fillcolor"] = "#b7f7b7"
                attrs["color"] = "#6cbf6c"

            # Router nodes get a distinct style
            if isinstance(node, RouterNode):
                attrs.setdefault("shape", "box")
                attrs.setdefault("style", "filled,rounded")

            dot.node(str(node.uid), label=node.name, **attrs)

        # add edges
        for u, v in self.successors.items():
            dot.edge(str(u.uid), str(v.uid))

        # add router edges (blue accent)
        for node in all_nodes:
            if isinstance(node, RouterNode):
                for key, target in node.node_map.items():
                    dot.edge(
                        str(node.uid),
                        str(target.uid),
                        label=str(key),
                        color="#4a90e2",
                        fontcolor="#4a90e2",
                        arrowsize="0.9",
                    )

        dot.render(filename, view=view, format="png")
        return dot

    @staticmethod
    def _expand_single_nodes_to_edges(
        edges: list[NodeBase | tuple[NodeBase, NodeBase]]
    ) -> list[tuple[NodeBase, NodeBase]]:
        """
        Normalize a mixed list of nodes and (node,node) tuples into
        a flat list of explicit edge tuples.

        Examples:
            [A, B, C] -> [(A, B), (B, C)]
            [A, (A, X), X, Y] -> [(A, X), (X, Y)]
            [(A, B), (B, C)] -> unchanged
        """
        normalized: list[tuple[NodeBase, NodeBase]] = []
        prev: NodeBase | None = None

        for item in edges:
            if isinstance(item, tuple):
                u, v = item
                normalized.append((u, v))
                prev = v
                continue

            if isinstance(item, NodeBase):
                if prev is not None:
                    normalized.append((prev, item))
                prev = item
                continue

            raise TypeError(f"Edge list items must be NodeBase or (NodeBase, NodeBase), got {type(item)}")

        return normalized
