from dataclasses import dataclass

from llmbrix.graph.graph_state import GraphState
from llmbrix.graph.node_base import NodeBase


@dataclass
class GraphRunContext:
    """
    Context during Graph execution. Updated by Graph in real time.
    Utilized by middleware functions to alter state of Graph execution.
    """

    node: NodeBase | None  # Node that is currently being executed
    state: GraphState  # state object used by nodes to write/read values from
    step: int  # step number - 0 = not started, 1 = execution of first Node, increases with each new visited node

    # if None Graph is still running.
    # if str Graph run was finished and reason for finishing is written by the Graph here
    finish_reason: str | None = None
