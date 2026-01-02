import pytest

from llmbrix.graph.graph import Graph
from llmbrix.graph.graph_run_context import GraphRunContext
from llmbrix.graph.graph_state import GraphState
from llmbrix.graph.node import Node
from llmbrix.graph.router_node import RouterNode


@Node
def n_set_a(s: GraphState):
    s.a = True


@Node
def n_set_b(s: GraphState):
    s.b = True


@Node
def n_inc(s: GraphState):
    s.x = s.get("x", 0) + 1


@Node
def n_stop(s: GraphState):
    pass


def test_expand_single_nodes_to_edges_basic():
    A, B, C = n_set_a, n_set_b, n_inc
    steps = [A, B, C]
    edges = Graph._expand_single_nodes_to_edges(steps)
    assert edges == [(A, B), (B, C)]


def test_expand_mixed_nodes_edges():
    A, X, Y = n_set_a, n_inc, n_stop
    steps = [A, (A, X), X, Y]
    edges = Graph._expand_single_nodes_to_edges(steps)
    assert edges == [(A, X), (X, Y)]


def test_reject_wrong_items():
    with pytest.raises(TypeError):
        Graph._expand_single_nodes_to_edges([123])


def test_graph_executes_linear_nodes_in_order():
    s = GraphState({"x": 0})
    graph = Graph(start_node=n_set_a, steps=[n_set_a, n_inc, n_set_b, n_stop])
    ctx = graph.run(s)
    assert s.a is True
    assert s.b is True
    assert s.x == 1
    assert ctx.finish_reason == "last_node"
    assert ctx.node is None


def test_graph_run_iter_yields_correct_number_of_steps():
    def snapshot(ctx: GraphRunContext):
        return {
            "node": ctx.node,
            "step": ctx.step,
            "finish_reason": ctx.finish_reason,
            "state": dict(ctx.state._data),  # shallow copy only
        }

    s = GraphState({})
    graph = Graph(start_node=n_set_a, steps=[n_set_a, n_set_b, n_stop])
    yielded = [snapshot(ctx) for ctx in graph.run_iter(s)]

    assert len(yielded) == 4
    assert yielded[0]["node"] == n_set_a
    assert yielded[1]["node"] == n_set_b
    assert yielded[2]["node"] == n_stop
    assert yielded[3]["node"] is None

    final_ctx = graph.run(s)
    assert final_ctx.finish_reason == "last_node"


def test_step_limit_terminates_graph():
    s = GraphState({"x": 0})
    graph = Graph(start_node=n_inc, steps=[n_inc, n_inc], step_limit=3)
    ctx = graph.run(s)
    assert s.x == 3
    assert ctx.finish_reason == "step_limit"
    assert ctx.node is None


def test_middleware_can_modify_context():
    def mw(ctx: GraphRunContext):
        if ctx.step == 0:
            return GraphRunContext(node=n_set_b, state=ctx.state, step=ctx.step)
        return ctx

    s = GraphState({})
    graph = Graph(start_node=n_set_a, steps=[n_set_a, n_set_b, n_stop], middleware=mw)
    ctx = graph.run(s)
    assert getattr(s, "a", None) is None
    assert s.b is True
    assert ctx.finish_reason == "last_node"


def test_middleware_can_terminate_graph():
    def mw(ctx):
        return GraphRunContext(node=None, state=ctx.state, step=ctx.step, finish_reason="middleware")

    s = GraphState({})
    graph = Graph(start_node=n_set_a, steps=[n_set_a, n_set_b], middleware=mw)
    yielded = list(graph.run_iter(s))
    assert yielded[-1].finish_reason == "middleware"
    assert yielded[-1].node is None


def test_router_node_selects_correct_branch():
    router = RouterNode(
        state_key="x",
        node_map={
            0: n_inc,
            1: n_inc,
            2: n_set_b,
        },
    )

    s = GraphState({"x": 0})
    graph = Graph(start_node=n_inc, steps=[n_inc, router], step_limit=10)
    ctx = graph.run(s)

    assert s.x == 2
    assert s.b is True
    assert ctx.finish_reason == "last_node"


def test_visualize_returns_bytes():
    GraphState({})
    graph = Graph(start_node=n_set_a, steps=[n_set_a, n_set_b])
    data = graph.visualize()
    assert isinstance(data, bytes)
    assert len(data) > 10


def test_router_cannot_be_edge_source():
    router = RouterNode("x", {})
    with pytest.raises(ValueError):
        Graph(start_node=n_set_a, steps=[(router, n_set_b)])


def test_multiple_successors_not_allowed():
    with pytest.raises(ValueError):
        Graph(
            start_node=n_set_a,
            steps=[(n_set_a, n_set_b), (n_set_a, n_stop)],
        )
