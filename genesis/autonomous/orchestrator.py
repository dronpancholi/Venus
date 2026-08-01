from __future__ import annotations

import time
from typing import Any

from genesis.autonomous.cycle import AutonomousEngine, CYCLE_ORDER, CycleRun, CycleStage
from genesis.execution.engine import ExecutionEngine
from genesis.fabric.kernel import FabricKernel
from genesis.graph_v2.core import LayerType, UnifiedGraph
from genesis.ued.database import Database


class EngineeringOrchestrator:
    """Orchestrator that wires platform services into the autonomous cycle."""

    def __init__(self, fabric: FabricKernel | None = None,
                 graph: UnifiedGraph | None = None,
                 ued: Database | None = None,
                 execution: ExecutionEngine | None = None):
        self._fabric = fabric or FabricKernel.instance()
        self._graph = graph or UnifiedGraph()
        self._ued = ued or Database()
        self._execution = execution or ExecutionEngine()
        self._engine = AutonomousEngine()
        self._register_default_handlers()

    def _register_default_handlers(self):
        self._engine.register(CycleStage.OBSERVE, self._observe)
        self._engine.register(CycleStage.ACQUIRE, self._acquire)
        self._engine.register(CycleStage.COMPILE, self._compile)
        self._engine.register(CycleStage.BUILD_IR, self._build_ir)
        self._engine.register(CycleStage.BUILD_TWIN, self._build_twin)
        self._engine.register(CycleStage.UPDATE_GRAPH, self._update_graph)
        self._engine.register(CycleStage.UPDATE_BRAIN, self._update_brain)
        self._engine.register(CycleStage.REASON, self._reason)
        self._engine.register(CycleStage.HYPOTHESIS, self._hypothesis)
        self._engine.register(CycleStage.PLAN, self._plan)
        self._engine.register(CycleStage.SIMULATE, self._simulate)
        self._engine.register(CycleStage.GENERATE_PATCH, self._generate_patch)
        self._engine.register(CycleStage.RUN_TESTS, self._run_tests)
        self._engine.register(CycleStage.BENCHMARK, self._benchmark)
        self._engine.register(CycleStage.VALIDATE, self._validate)
        self._engine.register(CycleStage.PUBLISH, self._publish)
        self._engine.register(CycleStage.LEARN, self._learn)

    def _observe(self, ctx: dict[str, Any]) -> dict[str, Any]:
        self._fabric.send("cycle.observe", {"timestamp": time.time()})
        return {"observed": True, "targets": ctx.get("targets", [])}

    def _acquire(self, ctx: dict[str, Any]) -> dict[str, Any]:
        self._fabric.send("cycle.acquire", {})
        return {"acquired": True}

    def _compile(self, ctx: dict[str, Any]) -> dict[str, Any]:
        self._fabric.send("cycle.compile", {})
        return {"compiled": True}

    def _build_ir(self, ctx: dict[str, Any]) -> dict[str, Any]:
        structural = self._graph.create_layer("structural", LayerType.STRUCTURAL)
        dep = self._graph.create_layer("dependency", LayerType.DEPENDENCY)
        knowledge = self._graph.create_layer("knowledge", LayerType.KNOWLEDGE)
        return {
            "structural_nodes": structural.node_count(),
            "dependency_nodes": dep.node_count(),
            "knowledge_nodes": knowledge.node_count(),
        }

    def _build_twin(self, ctx: dict[str, Any]) -> dict[str, Any]:
        from genesis.meta.twin import WorkspaceTwin
        return {"twin_built": True}

    def _update_graph(self, ctx: dict[str, Any]) -> dict[str, Any]:
        snap = self._graph.snapshot()
        return {
            "total_nodes": snap.node_count,
            "total_edges": snap.edge_count,
            "snapshot_id": snap.id,
        }

    def _update_brain(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {"brain_updated": True}

    def _reason(self, ctx: dict[str, Any]) -> dict[str, Any]:
        self._fabric.send("cycle.reason", {})
        return {"reasoning_complete": True}

    def _hypothesis(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {"hypotheses": []}

    def _plan(self, ctx: dict[str, Any]) -> dict[str, Any]:
        wf = self._execution.workflows.create("cycle_plan")
        return {"plan_id": wf.id, "nodes": len(wf.nodes)}

    def _simulate(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {"simulated": True}

    def _generate_patch(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {"patches": []}

    def _run_tests(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {"tests_passed": 0, "tests_failed": 0}

    def _benchmark(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {"benchmarks": {}}

    def _validate(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {"valid": True, "certificate": ""}

    def _publish(self, ctx: dict[str, Any]) -> dict[str, Any]:
        self._fabric.send("cycle.publish", {"timestamp": time.time()})
        return {"published": True}

    def _learn(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {"learned": True, "insights": []}

    def run_cycle(self, context: dict[str, Any] | None = None) -> CycleRun:
        self._fabric.send("cycle.start", {"timestamp": time.time()})
        result = self._engine.run(context)
        self._fabric.send("cycle.complete", {
            "status": result.status,
            "duration_ms": result.duration_ms,
        })
        return result

    @property
    def engine(self) -> AutonomousEngine:
        return self._engine

    def summary(self) -> dict[str, Any]:
        return {
            "autonomous_engine": self._engine.summary(),
            "graph": self._graph.summary(),
        }
