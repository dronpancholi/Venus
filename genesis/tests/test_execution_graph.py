"""Tests for GENESIS Ω Phase 2 — Execution Graph."""

import json
import tempfile
from pathlib import Path

from genesis.execution_graph import (
    ExecutionGraph, ExecutionNode, ExecutionEdge, ExecutionEngine,
    ExecutionGraphMonitor, ExecutionTrace, NodeType, EdgeType, NodeStatus,
    build_default_execution_graph,
)


class TestExecutionNode:
    def test_create(self):
        node = ExecutionNode(name="boot", node_type=NodeType.BOOT)
        assert node.name == "boot"
        assert node.node_type == NodeType.BOOT
        assert node.status == NodeStatus.PENDING

    def test_to_dict(self):
        node = ExecutionNode(name="test", node_type=NodeType.CUSTOM,
                             tags={"env": "prod"})
        d = node.to_dict()
        assert d["name"] == "test"
        assert d["node_type"] == "custom"
        assert d["tags"] == {"env": "prod"}


class TestExecutionEdge:
    def test_create(self):
        edge = ExecutionEdge(source="a", target="b")
        assert edge.source == "a"
        assert edge.target == "b"
        assert edge.edge_type == EdgeType.SEQUENTIAL

    def test_to_dict(self):
        edge = ExecutionEdge(source="a", target="b", condition="x > 0")
        d = edge.to_dict()
        assert d["condition"] == "x > 0"


class TestExecutionGraph:
    def test_add_and_get_node(self):
        g = ExecutionGraph()
        node = g.add_node(ExecutionNode("test"))
        assert g.get_node("test") is node
        assert g.get_node("missing") is None

    def test_add_edge_validates_nodes(self):
        g = ExecutionGraph()
        g.add_node(ExecutionNode("a"))
        g.add_node(ExecutionNode("b"))
        edge = g.add_edge(ExecutionEdge("a", "b"))
        assert edge.source == "a"

    def test_add_edge_invalid_raises(self):
        g = ExecutionGraph()
        g.add_node(ExecutionNode("a"))
        try:
            g.add_edge(ExecutionEdge("a", "missing"))
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_connect(self):
        g = ExecutionGraph()
        g.add_node(ExecutionNode("a"))
        g.add_node(ExecutionNode("b"))
        edge = g.connect("a", "b", EdgeType.FEEDBACK, "test_condition")
        assert edge.edge_type == EdgeType.FEEDBACK
        assert edge.condition == "test_condition"

    def test_successors(self):
        g = ExecutionGraph()
        g.add_node(ExecutionNode("a"))
        g.add_node(ExecutionNode("b"))
        g.add_node(ExecutionNode("c"))
        g.connect("a", "b")
        g.connect("a", "c")
        succs = g.successors("a")
        assert len(succs) == 2
        assert {s.name for s in succs} == {"b", "c"}

    def test_predecessors(self):
        g = ExecutionGraph()
        g.add_node(ExecutionNode("a"))
        g.add_node(ExecutionNode("b"))
        g.connect("a", "b")
        preds = g.predecessors("b")
        assert len(preds) == 1
        assert preds[0].name == "a"

    def test_topological_order(self):
        g = ExecutionGraph()
        g.add_node(ExecutionNode("a"))
        g.add_node(ExecutionNode("b"))
        g.add_node(ExecutionNode("c"))
        g.connect("a", "b")
        g.connect("b", "c")
        order = g.topological_order()
        names = [n.name for n in order]
        assert names.index("a") < names.index("b")
        assert names.index("b") < names.index("c")

    def test_edge_filtering(self):
        g = ExecutionGraph()
        g.add_node(ExecutionNode("a"))
        g.add_node(ExecutionNode("b"))
        g.add_node(ExecutionNode("c"))
        g.connect("a", "b")
        g.connect("b", "c")
        assert len(g.get_edges(from_node="a")) == 1
        assert len(g.get_edges(to_node="c")) == 1

    def test_to_dict(self):
        g = build_default_execution_graph()
        d = g.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert "topological_order" in d
        assert len(d["nodes"]) == 14
        assert len(d["edges"]) >= 13

    def test_save_and_load(self):
        g = build_default_execution_graph()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            g.save(f.name)
            data = json.loads(Path(f.name).read_text())
        assert data["name"] == "genesis_execution_graph"


class TestBuildDefaultExecutionGraph:
    def test_all_nodes_present(self):
        g = build_default_execution_graph()
        expected_types = [
            "boot", "runtime", "scheduler", "planner", "brain",
            "memory", "execution", "compiler", "verification", "graph",
            "economics", "learning", "evolution", "shutdown",
        ]
        for name in expected_types:
            assert g.get_node(name) is not None, f"Missing node: {name}"

    def test_boot_to_shutdown_path(self):
        g = build_default_execution_graph()
        order = [n.name for n in g.topological_order()]
        assert order.index("boot") < order.index("shutdown")

    def test_feedback_loops(self):
        g = build_default_execution_graph()
        feedback_edges = g.get_edges()
        feedback_types = [e.edge_type for e in feedback_edges]
        assert EdgeType.FEEDBACK in feedback_types


class TestExecutionTrace:
    def test_create(self):
        trace = ExecutionTrace()
        assert trace.trace_id.startswith("trace_")
        assert trace.started_at != ""

    def test_duration_zero_if_not_completed(self):
        trace = ExecutionTrace()
        assert trace.duration() == 0.0

    def test_to_dict(self):
        trace = ExecutionTrace()
        d = trace.to_dict()
        assert "trace_id" in d
        assert "nodes" in d


class TestExecutionEngine:
    def test_execute_full_graph(self):
        engine = ExecutionEngine()
        trace = engine.execute()
        assert len(trace.nodes) > 0
        assert trace.completed_at != ""

    def test_execute_mid_graph(self):
        engine = ExecutionEngine()
        trace = engine.execute(start_node="brain")
        assert "boot" not in trace.nodes
        assert "brain" in trace.nodes

    def test_current_trace(self):
        engine = ExecutionEngine()
        assert engine.current_trace() is None
        trace = engine.execute()
        assert engine.current_trace() is None  # cleared after completion


class TestExecutionGraphMonitor:
    def test_monitor_recent_traces(self):
        g = build_default_execution_graph()
        engine = ExecutionEngine(g)
        monitor = ExecutionGraphMonitor(engine)
        t1 = engine.execute()
        monitor.record_trace(t1)
        t2 = engine.execute()
        monitor.record_trace(t2)
        assert monitor.total_executions() == 2
        assert len(monitor.recent_traces(1)) == 1

    def test_latest_trace(self):
        g = build_default_execution_graph()
        engine = ExecutionEngine(g)
        monitor = ExecutionGraphMonitor(engine)
        assert monitor.latest_trace() is None
        t = engine.execute()
        monitor.record_trace(t)
        assert monitor.latest_trace() is not None

    def test_average_duration(self):
        g = build_default_execution_graph()
        engine = ExecutionEngine(g)
        monitor = ExecutionGraphMonitor(engine)
        monitor.record_trace(engine.execute())
        monitor.record_trace(engine.execute())
        assert monitor.average_duration() > 0

    def test_summary(self):
        g = build_default_execution_graph()
        engine = ExecutionEngine(g)
        monitor = ExecutionGraphMonitor(engine)
        s = monitor.summary()
        assert "total_executions" in s
        assert "average_duration" in s
        assert "node_failures" in s
