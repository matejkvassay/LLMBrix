import uuid

from llmbrix.graph.graph_state import GraphState
from llmbrix.graph.node_base import NodeBase


class RouterNode(NodeBase):
    """
    Decides what is next node to be executed based on a condition.
    Always 1 single node to continue Graph execution on will be chosen.
    """

    def __init__(self, state_key: str, node_map: dict[str, NodeBase], name: str = None):
        """
        :param state_key: Key in GraphState for str attribute used for decision.
        :param node_map: Map of str value -> NodeBase. Used to decide what is next node based on state_key value.
        :param name: Optional, human-readable name for this node. If not provided it will be based on the state_key.
        """
        uid = uuid.uuid4().int
        name = name or f"router_{state_key}"
        super().__init__(uid=uid, name=name)
        self.state_key = state_key
        self.node_map = node_map
        for k, v in node_map.items():
            if not isinstance(v, NodeBase):
                raise ValueError(f"RouterNode node_map value for key {k} must be a NodeBase, got {type(v)}")

    def run(self, state: GraphState) -> NodeBase:
        """
        Run this node. Used by Graph during execution.

        :param state: GraphState where state_key is looked for.
        :return: Routing decision - instance of NodeBase to continue Graph execution on.
        """
        value = state.read(self.state_key)
        if value not in self.node_map:
            raise ValueError(
                f'Value "{value}" not found in node map for router {self.name}. Available keys: {self.node_map.keys()}'
            )
        return self.node_map[value]
