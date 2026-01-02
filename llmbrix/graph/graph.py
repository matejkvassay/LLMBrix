from typing import Callable, Iterator

from graphviz import Digraph

from llmbrix.graph.graph_run_context import GraphRunContext
from llmbrix.graph.graph_state import GraphState
from llmbrix.graph.node import Node
from llmbrix.graph.node_base import NodeBase
from llmbrix.graph.router_node import RouterNode


class Graph:
    """
    Workflow execution Graph. Consists of steps where each step is a NodeBase instance.
    Graph executes these steps starting from start_node.

    Only simple DiGraph topologies are supported:
        - nodes connect to 1 other node in the workflow DiGraph
        - router nodes can connect to multiple nodes
        - during execution nodes always choose only 1 node to continue with based on a condition
        - no parallel branches are allowed, parallelism has to be handled within the Nodes
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
                        - Single nodes u, where u is NodeBase Instance
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
                - check if step limit not reached
                - apply middleware if set
                - check if any node is selected for execution, if not terminate with "last_node" reason
                - if selected node is Node then execute and find successor
                - if selected node is RouterNode then execute to define successor
            - return

        :param state: Initial GraphState passed to start_node.
        :yield: GraphRunContext for each execution step.

                Yield happens:
                    - just before a node is executed
                    - graph execution loop is about to terminate:
                        - last node is reached
                        - middleware decided to terminate
                        - step limit was reached

               Context before application of middleware is not yielded => the middleware is applied
               as pre-processor before step is executed.

               => Yielded value shows what step is going to be executed just now + last final yield of final context.

        :return: Iterator over GraphRunContext updates during Graph execution.
        """
        context = GraphRunContext(node=self.start_node, state=state, step=0)
        while True:
            if context.step >= self.step_limit:
                context.node = None
                context.finish_reason = "step_limit"
                yield context
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
                    yield modified_context
                    break
                context = modified_context
            node = context.node
            if node is None:
                context.finish_reason = "last_node"
                yield context
                break
            elif isinstance(node, Node):
                yield context
                node.run(context.state)
                if node in self.successors:
                    context.node = self.successors[node]
                else:
                    context.node = None
            elif isinstance(node, RouterNode):
                yield context
                context.node = node.run(context.state)
            else:
                raise TypeError(f"Unrecognized graph node type: {type(node)}")
            context.step += 1

    def visualize(self, context: GraphRunContext | None = None, fmt: str = "png") -> bytes:
        """
        Visualizes the Graph using Graphviz and returns image bytes.

        Display in Jupyter cell:
            ```python
            from IPython.display import Image, display

            # inline graph visualization
            Image(graph.visualize())

            # in a loop showing active graph execution
            for ctx in graph.run_iter(state):
                display(Image(graph.visualize(context=ctx)))
            ```

        :param context: Optional GraphRunContext used to highlight the active "to be executed" node.
        :param fmt: Output image format ('png', 'svg', etc.).
        :return: Image bytes rendered by Graphviz.
        """
        dot = Digraph(comment="Graph")
        dot.graph_attr.update(
            {
                "rankdir": "LR",
                "splines": "spline",
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
        all_nodes: set[NodeBase] = set(self.successors.keys())
        all_nodes.update(self.successors.values())
        for node in list(all_nodes):
            if isinstance(node, RouterNode):
                all_nodes.update(node.node_map.values())
        for node in all_nodes:
            attrs = {}

            if context is not None and context.node == node:
                attrs["fillcolor"] = "#b7f7b7"
                attrs["color"] = "#6cbf6c"

            if isinstance(node, RouterNode):
                attrs.setdefault("shape", "box")
                attrs.setdefault("style", "filled,rounded")

            dot.node(str(node.uid), label=node.name, **attrs)
        for u, v in self.successors.items():
            dot.edge(str(u.uid), str(v.uid))
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
        return dot.pipe(format=fmt)

    @staticmethod
    def _expand_single_nodes_to_edges(
        steps: list[NodeBase | tuple[NodeBase, NodeBase]]
    ) -> list[tuple[NodeBase, NodeBase]]:
        """
        Normalize a mixed list of nodes and (node,node) tuples into
        a flat list of explicit edge tuples.

        Examples:
            [A, B, C] -> [(A, B), (B, C)]
            [A, (A, X), X, Y] -> [(A, X), (X, Y)]
            [(A, B), (B, C)] -> unchanged

        :param steps: List of nodes/edges defining topography of the graph.
        :return: List of tuples with edges.
        """
        normalized: list[tuple[NodeBase, NodeBase]] = []
        prev: NodeBase | None = None

        for item in steps:
            if isinstance(item, tuple):
                u, v = item
                normalized.append((u, v))
                prev = None
                continue

            if isinstance(item, NodeBase):
                if prev is not None:
                    normalized.append((prev, item))
                prev = item
                continue

            raise TypeError(f"Edge list items must be NodeBase or (NodeBase, NodeBase), got {type(item)}")

        return normalized
