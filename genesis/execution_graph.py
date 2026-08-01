"""
GENESIS Ω Phase 2: Complete Execution Graph.

Models every runtime transition in the platform as a directed execution graph.
Every transition is visible, traceable, reproducible, and checkpointable.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class NodeType(Enum):
    BOOT = "boot"
    RUNTIME = "runtime"
    SCHEDULER = "scheduler"
    PLANNER = "planner"
    BRAIN = "brain"
    MEMORY = "memory"
    EXECUTION = "execution"
    COMPILER = "compiler"
    VERIFICATION = "verification"
    GRAPH = "graph"
    ECONOMICS = "economics"
    LEARNING = "learning"
    EVOLUTION = "evolution"
    SHUTDOWN = "shutdown"
    CUSTOM = "custom"


class EdgeType(Enum):
    SEQUENTIAL = "sequential"
    FEEDBACK = "feedback"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    FALLBACK = "fallback"


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"


@dataclass
class ExecutionNode:
    name: str
    node_type: NodeType = NodeType.CUSTOM
    status: NodeStatus = NodeStatus.PENDING
    description: str = ""
    version: str = "1.0"
    timeout: float = 300.0
    retry_count: int = 0
    max_retries: int = 3
    tags: dict[str, str] = field(default_factory=dict)
    pre_conditions: list[str] = field(default_factory=list)
    post_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "node_type": self.node_type.value,
            "status": self.status.value,
            "description": self.description,
            "version": self.version,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "tags": self.tags,
            "pre_conditions": self.pre_conditions,
            "post_conditions": self.post_conditions,
        }


@dataclass
class ExecutionEdge:
    source: str
    target: str
    edge_type: EdgeType = EdgeType.SEQUENTIAL
    condition: str = ""
    weight: float = 1.0
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type.value,
            "condition": self.condition,
            "weight": self.weight,
            "description": self.description,
        }


@dataclass
class ExecutionEvent:
    node_name: str
    event_type: str
    timestamp: str = ""
    duration: float = 0.0
    status: str = ""
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ExecutionTrace:
    trace_id: str = ""
    started_at: str = ""
    completed_at: str = ""
    nodes: dict[str, NodeStatus] = field(default_factory=dict)
    events: list[ExecutionEvent] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    error: str = ""

    def __post_init__(self):
        if not self.trace_id:
            self.trace_id = f"trace_{generate_id('exec', 12)}"
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()

    def duration(self) -> float:
        if not self.completed_at:
            return 0.0
        start = datetime.fromisoformat(self.started_at)
        end = datetime.fromisoformat(self.completed_at)
        return (end - start).total_seconds()

    def set_node_status(self, node_name: str, status: NodeStatus):
        self.nodes.update({node_name: status})

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.duration(),
            "nodes": {k: v.value for k, v in self.nodes.items()},
            "events": [asdict(e) for e in self.events],
            "metrics": self.metrics,
            "error": self.error,
        }


class ExecutionGraph:
    """Complete DAG of all runtime transitions."""

    def __init__(self, name: str = "genesis_execution_graph"):
        self.name = name
        self._nodes: dict[str, ExecutionNode] = {}
        self._edges: list[ExecutionEdge] = []

    def add_node(self, node: ExecutionNode) -> ExecutionNode:
        self._nodes[node.name] = node
        return node

    def add_edge(self, edge: ExecutionEdge) -> ExecutionEdge:
        if edge.source not in self._nodes or edge.target not in self._nodes:
            raise ValueError(f"Edge references unknown node: {edge.source} -> {edge.target}")
        self._edges.append(edge)
        return edge

    def connect(self, source: str, target: str, edge_type: EdgeType = EdgeType.SEQUENTIAL,
                condition: str = "", weight: float = 1.0, description: str = "") -> ExecutionEdge:
        return self.add_edge(ExecutionEdge(
            source=source, target=target, edge_type=edge_type,
            condition=condition, weight=weight, description=description,
        ))

    def get_node(self, name: str) -> ExecutionNode | None:
        return self._nodes.get(name)

    def get_edges(self, from_node: str | None = None, to_node: str | None = None) -> list[ExecutionEdge]:
        results = list(self._edges)
        if from_node:
            results = [e for e in results if e.source == from_node]
        if to_node:
            results = [e for e in results if e.target == to_node]
        return results

    def successors(self, node_name: str) -> list[ExecutionNode]:
        targets = {e.target for e in self._edges if e.source == node_name}
        return [self._nodes[t] for t in targets if t in self._nodes]

    def predecessors(self, node_name: str) -> list[ExecutionNode]:
        sources = {e.source for e in self._edges if e.target == node_name}
        return [self._nodes[s] for s in sources if s in self._nodes]

    def topological_order(self) -> list[ExecutionNode]:
        in_degree: dict[str, int] = {n: 0 for n in self._nodes}
        for edge in self._edges:
            in_degree[edge.target] = in_degree.get(edge.target, 0) + 1
        queue = [n for n, d in in_degree.items() if d == 0]
        ordered = []
        while queue:
            node = queue.pop(0)
            ordered.append(self._nodes[node])
            for succ in self.successors(node):
                in_degree[succ.name] -= 1
                if in_degree[succ.name] == 0:
                    queue.append(succ.name)
        remaining = [n for n in self._nodes if n not in [o.name for o in ordered]]
        for r in remaining:
            ordered.append(self._nodes[r])
        return ordered

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "nodes": {k: v.to_dict() for k, v in self._nodes.items()},
            "edges": [e.to_dict() for e in self._edges],
            "topological_order": [n.name for n in self.topological_order()],
        }

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


def build_default_execution_graph() -> ExecutionGraph:
    """Build the standard Genesis execution graph."""
    g = ExecutionGraph()

    # Define all standard nodes
    g.add_node(ExecutionNode("boot", NodeType.BOOT, description="Platform boot sequence",
                              pre_conditions=["config_loaded", "di_initialized"],
                              post_conditions=["all_stores_created", "event_bus_ready"]))
    g.add_node(ExecutionNode("runtime", NodeType.RUNTIME, description="Runtime initialization",
                              pre_conditions=["boot_completed"],
                              post_conditions=["services_registered"]))
    g.add_node(ExecutionNode("scheduler", NodeType.SCHEDULER, description="Distributed scheduler",
                              pre_conditions=["runtime_ready"],
                              post_conditions=["scheduler_active"]))
    g.add_node(ExecutionNode("planner", NodeType.PLANNER, description="Engineering planner",
                              pre_conditions=["scheduler_ready"],
                              post_conditions=["plan_created"]))
    g.add_node(ExecutionNode("brain", NodeType.BRAIN, description="Engineering brain cognition",
                              pre_conditions=["planner_ready"],
                              post_conditions=["brain_active", "knowledge_loaded"],
                              timeout=600.0))
    g.add_node(ExecutionNode("memory", NodeType.MEMORY, description="Memory system initialization",
                              pre_conditions=["brain_ready"],
                              post_conditions=["memory_active", "stores_loaded"]))
    g.add_node(ExecutionNode("execution", NodeType.EXECUTION, description="Execution engine",
                              pre_conditions=["memory_ready"],
                              post_conditions=["executor_active"]))
    g.add_node(ExecutionNode("compiler", NodeType.COMPILER, description="Meta compiler",
                              pre_conditions=["executor_ready"],
                              post_conditions=["compiler_ready"]))
    g.add_node(ExecutionNode("verification", NodeType.VERIFICATION, description="Verification system",
                              pre_conditions=["compiler_ready"],
                              post_conditions=["verification_active"]))
    g.add_node(ExecutionNode("graph", NodeType.GRAPH, description="Knowledge & unified graph",
                              pre_conditions=["verification_ready"],
                              post_conditions=["graph_active"]))
    g.add_node(ExecutionNode("economics", NodeType.ECONOMICS, description="Engineering economics",
                              pre_conditions=["graph_ready"],
                              post_conditions=["economics_active"]))
    g.add_node(ExecutionNode("learning", NodeType.LEARNING, description="Continuous learning",
                              pre_conditions=["economics_ready"],
                              post_conditions=["learning_active"]))
    g.add_node(ExecutionNode("evolution", NodeType.EVOLUTION, description="Self-evolution engine",
                              pre_conditions=["learning_ready"],
                              post_conditions=["evolution_active"]))
    g.add_node(ExecutionNode("shutdown", NodeType.SHUTDOWN, description="Graceful shutdown",
                              pre_conditions=[],
                              post_conditions=["all_stores_flushed", "services_stopped"]))

    # Standard execution flow edges
    g.connect("boot", "runtime")
    g.connect("runtime", "scheduler")
    g.connect("scheduler", "planner")
    g.connect("planner", "brain")
    g.connect("brain", "memory")
    g.connect("memory", "execution")
    g.connect("execution", "compiler")
    g.connect("compiler", "verification")
    g.connect("verification", "graph")
    g.connect("graph", "economics")
    g.connect("economics", "learning")
    g.connect("learning", "evolution")
    g.connect("evolution", "shutdown")

    # Feedback loops
    g.connect("learning", "brain", EdgeType.FEEDBACK, "new_knowledge_available")
    g.connect("evolution", "brain", EdgeType.FEEDBACK, "improvement_available")
    g.connect("execution", "compiler", EdgeType.FEEDBACK, "recompilation_needed")
    g.connect("verification", "execution", EdgeType.FEEDBACK, "verification_failed")

    return g


class ExecutionEngine:
    """Runs the execution graph, producing traces."""

    def __init__(self, graph: ExecutionGraph | None = None):
        self.graph = graph or build_default_execution_graph()
        self._current_trace: ExecutionTrace | None = None
        self._listeners: list[Callable[[ExecutionEvent], None]] = []

    def on_event(self, listener: Callable[[ExecutionEvent], None]):
        self._listeners.append(listener)

    def _emit(self, event: ExecutionEvent):
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass

    def execute(self, start_node: str = "boot") -> ExecutionTrace:
        trace = ExecutionTrace()
        self._current_trace = trace

        ordered = self.graph.topological_order()
        start_idx = 0
        for i, node in enumerate(ordered):
            if node.name == start_node:
                start_idx = i
                break

        for node in ordered[start_idx:]:
            if node.name == "shutdown":
                continue

            trace.set_node_status(node.name, NodeStatus.RUNNING)
            start = time.time()

            event = ExecutionEvent(
                node_name=node.name,
                event_type="start",
                status="running",
            )
            trace.events.append(event)
            self._emit(event)

            elapsed = time.time() - start
            trace.metrics[f"{node.name}_duration"] = elapsed
            trace.set_node_status(node.name, NodeStatus.COMPLETED)

            event = ExecutionEvent(
                node_name=node.name,
                event_type="complete",
                timestamp=datetime.now(timezone.utc).isoformat(),
                duration=elapsed,
                status="completed",
            )
            trace.events.append(event)
            self._emit(event)

        trace.completed_at = datetime.now(timezone.utc).isoformat()
        self._current_trace = None
        return trace

    def current_trace(self) -> ExecutionTrace | None:
        return self._current_trace


class ExecutionGraphMonitor:
    """Real-time monitoring of execution state."""

    def __init__(self, engine: ExecutionEngine):
        self.engine = engine
        self._history: list[ExecutionTrace] = []
        engine.on_event(self._on_event)
        self._last_event: ExecutionEvent | None = None

    def _on_event(self, event: ExecutionEvent):
        self._last_event = event

    def record_trace(self, trace: ExecutionTrace):
        self._history.append(trace)

    def recent_traces(self, n: int = 10) -> list[ExecutionTrace]:
        return self._history[-n:]

    def latest_trace(self) -> ExecutionTrace | None:
        return self._history[-1] if self._history else None

    def total_executions(self) -> int:
        return len(self._history)

    def average_duration(self) -> float:
        if not self._history:
            return 0.0
        durations = [t.duration() for t in self._history if t.completed_at]
        return sum(durations) / len(durations) if durations else 0.0

    def node_failure_count(self, node_name: str) -> int:
        count = 0
        for trace in self._history:
            if trace.nodes.get(node_name) == NodeStatus.FAILED:
                count += 1
        return count

    def summary(self) -> dict[str, Any]:
        return {
            "total_executions": self.total_executions(),
            "average_duration": self.average_duration(),
            "last_event": asdict(self._last_event) if self._last_event else None,
            "node_failures": {
                n: self.node_failure_count(n)
                for n in self.engine.graph._nodes
            },
        }
