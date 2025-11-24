import uuid
from collections import defaultdict
from typing import Callable


class State:
    def __init__(self):
        self.data = dict()

    def __getitem__(self, item):
        return self.read(item)

    def write(self, key=None, value=None, **kwargs):
        if key:
            self.data[key] = value
        else:
            self.data.update(kwargs)

    def read(self, key):
        return self.data[key]


class Node:
    def __init__(self, name: str, func: Callable[[State], None]):
        self.uid = uuid.uuid4()
        self.name = name
        self.func = func

    def run(self, state: State):
        self.func(state)


class Edge:
    def __init__(self, src: Node, dst: Node, cond: Callable[[State], None] = None):
        self.src = src
        self.dst = dst
        self.cond = cond


class Graph:
    def __init__(self, start_node: Node, edges: list[tuple[Node, Node] | tuple[Node, Node, Callable[[State], bool]]]):
        self.start_node = start_node

        self.conditions = dict()
        self.successors = defaultdict(list)
        # add check - if more than 1 successor => all of them have to define condition
        # check if conditional edge has more than 1 destinations (otherwise it will end exec)
        for edge in edges:
            if len(edge) == 2:
                src, dst, cond = edge[0], edge[1], None
            elif len(edge) == 3:
                src, dst, cond = edge
            else:
                raise ValueError("Edge has to be either tuple of (Node, Node) or triple of (Node,Node,Callable)")
            self.successors[src].append(dst)
            if cond:
                self.conditions[(src, dst)] = cond
            # add check - if more than 1 successor => all of them have to define condition
            # check if conditional edge has more than 1 destinations (otherwise it will end exec)

    def run(self, state: State):
        step = 0
        node = self.start_node
        while node:
            step += 1
            state.write("step_no", step)
            node.run(state)
            successors = self.successors.get(node)
            next_node = None
            if not successors:
                state.write({"finished": True, "finished_on": str(node)})
            elif len(successors) == 1:
                next_node = successors[0]
            else:
                for v in successors:
                    if self.conditions[(node, v)]:
                        next_node = v
                        break
                if not next_node:
                    raise ValueError("All conditions returned False.")
            state.write("next_node", str(next_node) if next_node else None)
            node = next_node
