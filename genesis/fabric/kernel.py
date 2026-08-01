from __future__ import annotations

import json
import queue
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.fabric.audit import AuditLog
from genesis.fabric.bus import Message, MessageBus
from genesis.fabric.context import Context
from genesis.fabric.discovery import ServiceHealth, ServiceInstance, ServiceRegistry
from genesis.fabric.events import (
    EngineeringEvent, EventPriority, EventRouter, EventSeverity, EventStore,
)
from genesis.fabric.metrics import FabricMetrics
from genesis.fabric.policy import PolicyEngine
from genesis.fabric.scheduler import DistributedScheduler
from genesis.fabric.storage import StorageEngine
from genesis.engineering import EngineeringObject, EngineeringObjectType, EngineeringRegistry, get_registry
from genesis.utils.identity import generate_id
from genesis.boot.engine import BootEngine, BootPhase, BootReport
from genesis.health.engine import SystemHealthEngine, HealthEntry, HealthDimension, HealthCollector
from genesis.observability.engine import ObservabilityEngine, ActionType, ActionSeverity
from genesis.graph_core.engine import (
    CanonicalGraph, GraphRegistry,
    GraphV2Adapter, GraphDBAdapter, HypergraphAdapter,
    KnowledgeGraphAdapter, ExecutionGraphAdapter, MetaGraphAdapter,
)

# These are imported lazily in boot() to avoid circular imports
# AgentRuntime, TaskGraph, AgentExecutionEngine, TaskExecutor


class KernelState(Enum):
    BOOTING = "booting"
    RUNNING = "running"
    DEGRADED = "degraded"
    SHUTDOWN = "shutdown"


@dataclass
class KernelStats:
    services: int = 0
    messages_sent: int = 0
    messages_dropped: int = 0
    active_sessions: int = 0
    uptime_seconds: float = 0.0
    threads: int = 0
    state: str = ""
    events_delivered: int = 0
    event_store_count: int = 0
    executor_running: bool = False
    executor_executions: int = 0
    executor_failed: int = 0


class FabricKernel:
    """Central fabric kernel. Every subsystem registers here.

    All communication flows through the Fabric:
      Subsystem → Fabric → Destination

    All state is optionally persisted to SQLite via StorageEngine.
    """

    _instance: FabricKernel | None = None

    @classmethod
    def instance(cls, storage_path: str | None = None, enable_persistence: bool = True) -> FabricKernel:
        if cls._instance is None:
            cls._instance = cls(storage_path=storage_path, enable_persistence=enable_persistence)
        return cls._instance

    def __init__(self, storage_path: str | None = None, enable_persistence: bool = True):
        if FabricKernel._instance is not None:
            raise RuntimeError("FabricKernel is a singleton. Use FabricKernel.instance()")
        FabricKernel._instance = self

        self.state = KernelState.BOOTING
        self._started_at = time.time()
        self._bus = MessageBus()
        self._event_router = EventRouter(EventStore(max_events=50000))
        self._registry = ServiceRegistry()
        self._scheduler = DistributedScheduler()
        self._policy = PolicyEngine()
        self._metrics = FabricMetrics(kernel=self)
        self._audit = AuditLog(kernel=self)
        self._contexts: dict[str, Context] = {}
        self._lock = threading.RLock()
        self._hooks: dict[str, list[Callable]] = defaultdict(list)
        self._threads: list[threading.Thread] = []
        self._storage: StorageEngine | None = None
        self._agent_runtime: Any = None  # AgentRuntime (lazy)
        self._task_graph: Any = None     # TaskGraph (lazy)
        self._execution_engine: Any = None  # AgentExecutionEngine (lazy)
        self._task_executor: Any = None  # TaskExecutor (lazy)
        self._engineering: EngineeringRegistry = get_registry()
        self._knowledge: Any = None
        self._reasoning: Any = None
        self._copilot: Any = None
        self._timeline: Any = None
        self._workspace_loaded: bool = False
        self._continuous_engineering: Any = None
        self._autonomous_review: Any = None
        self._twin: Any = None
        self._ai: Any = None
        self._automation: Any = None
        self._observatory: Any = None
        self._explorer: Any = None
        self._planner: Any = None
        self._memory_v2: Any = None
        self._multi_project: Any = None
        self._live_architecture: Any = None
        self._visual_reasoning: Any = None
        self._agentos: Any = None
        self._command_center: Any = None
        self._state_engine: Any = None
        self._nervous_system: Any = None
        self._context_engine: Any = None
        self._workflow_engine: Any = None
        self._insight_engine: Any = None
        self._decision_intelligence: Any = None
        self._knowledge_organizer: Any = None
        self._proactive_copilot: Any = None
        self._playbooks: Any = None
        self._app_platform: Any = None
        self._sdk: Any = None
        self._boot_engine: BootEngine | None = None
        self._health_engine: SystemHealthEngine | None = None
        self._observability: ObservabilityEngine | None = None
        self._graph_registry: GraphRegistry | None = None

        if enable_persistence:
            self._storage = StorageEngine(storage_path)

    @property
    def bus(self) -> MessageBus:
        return self._bus

    @property
    def events(self) -> EventRouter:
        return self._event_router

    @property
    def event_store(self) -> EventStore:
        return self._event_router._store

    @property
    def registry(self) -> ServiceRegistry:
        return self._registry

    @property
    def scheduler(self) -> DistributedScheduler:
        return self._scheduler

    @property
    def policy(self) -> PolicyEngine:
        return self._policy

    @property
    def metrics(self) -> FabricMetrics:
        return self._metrics

    @property
    def audit(self) -> AuditLog:
        return self._audit

    @property
    def storage(self) -> StorageEngine | None:
        return self._storage

    @property
    def agent_runtime(self) -> Any:
        return self._agent_runtime

    @property
    def task_graph(self) -> Any:
        return self._task_graph

    @property
    def execution_engine(self) -> Any:
        return self._execution_engine

    @property
    def task_executor(self) -> Any:
        return self._task_executor

    @property
    def engineering(self) -> EngineeringRegistry:
        return self._engineering

    @property
    def knowledge(self) -> Any:
        if self._knowledge is None:
            from genesis.knowledge import KnowledgeEngine as _KE
            self._knowledge = _KE(kernel=self)
        return self._knowledge

    @property
    def reasoning(self) -> Any:
        if self._reasoning is None:
            from genesis.engineering.reasoning import EngineeringReasoningEngine as _RE
            self._reasoning = _RE()
        return self._reasoning

    @property
    def copilot(self) -> Any:
        if self._copilot is None:
            from genesis.engineering.copilot import CopilotEngine as _CE
            self._copilot = _CE(kernel=self)
        return self._copilot

    @property
    def timeline(self) -> Any:
        if self._timeline is None:
            from genesis.engineering.timeline import UniversalTimeline as _UT
            self._timeline = _UT(kernel=self)
        return self._timeline

    @property
    def autonomous_review(self) -> Any:
        if self._autonomous_review is None:
            from genesis.engineering.review import AutonomousReview as _AR
            self._autonomous_review = _AR(kernel=self)
        return self._autonomous_review

    @property
    def twin(self) -> Any:
        if self._twin is None:
            from genesis.twin import DigitalTwin as _DT
            self._twin = _DT(kernel=self)
        return self._twin

    @property
    def ai(self) -> Any:
        if self._ai is None:
            from genesis.ai.engine import AIOrchestrationEngine as _AI
            self._ai = _AI(kernel=self)
        return self._ai

    @property
    def automation(self) -> Any:
        if self._automation is None:
            from genesis.automation import AutomationEngine as _AE
            self._automation = _AE(kernel=self)
        return self._automation

    @property
    def observatory(self) -> Any:
        if self._observatory is None:
            from genesis.observatory import EngineeringObservatory as _EO
            self._observatory = _EO(kernel=self)
        return self._observatory

    @property
    def explorer(self) -> Any:
        if self._explorer is None:
            from genesis.explorer import EngineeringExplorer as _EE
            self._explorer = _EE(kernel=self)
        return self._explorer

    @property
    def planner(self) -> Any:
        if self._planner is None:
            from genesis.planner import EngineeringPlanner as _EP
            self._planner = _EP(kernel=self)
        return self._planner

    @property
    def memory_v2(self) -> Any:
        if self._memory_v2 is None:
            from genesis.memory_v2 import EngineeringMemoryV2 as _EM
            self._memory_v2 = _EM(kernel=self)
        return self._memory_v2

    @property
    def multi_project(self) -> Any:
        if self._multi_project is None:
            from genesis.multi_project import MultiProjectIntelligence as _MP
            self._multi_project = _MP(kernel=self)
        return self._multi_project

    @property
    def live_architecture(self) -> Any:
        if self._live_architecture is None:
            from genesis.architecture import LiveArchitectureEngine as _LA
            self._live_architecture = _LA(kernel=self)
        return self._live_architecture

    @property
    def visual_reasoning(self) -> Any:
        if self._visual_reasoning is None:
            from genesis.visual_reasoning import VisualReasoningEngine as _VR
            self._visual_reasoning = _VR(kernel=self)
        return self._visual_reasoning

    @property
    def agentos(self) -> Any:
        if self._agentos is None:
            from genesis.agentos import AgentOSFoundation as _AO
            self._agentos = _AO(kernel=self)
        return self._agentos

    @property
    def command_center(self) -> Any:
        if self._command_center is None:
            from genesis.command_center import LiveCommandCenter as _CC
            self._command_center = _CC(kernel=self)
        return self._command_center

    @property
    def state_engine(self) -> Any:
        if self._state_engine is None:
            from genesis.state import EngineeringState as _ES
            self._state_engine = _ES.instance()
            self._state_engine.set_kernel(self)
        return self._state_engine

    @property
    def nervous_system(self) -> Any:
        if self._nervous_system is None:
            from genesis.nervous import EngineeringNervousSystem as _NS
            self._nervous_system = _NS(kernel=self)
        return self._nervous_system

    @property
    def context_engine(self) -> Any:
        if self._context_engine is None:
            from genesis.context import ContextEngine as _CE
            self._context_engine = _CE(kernel=self)
        return self._context_engine

    @property
    def workflow_engine(self) -> Any:
        if self._workflow_engine is None:
            from genesis.workflows import EngineeringWorkflowEngine as _WE
            self._workflow_engine = _WE(kernel=self)
        return self._workflow_engine

    @property
    def insight_engine(self) -> Any:
        if self._insight_engine is None:
            from genesis.insight import EngineeringInsightEngine as _IE
            self._insight_engine = _IE(kernel=self)
        return self._insight_engine

    @property
    def decision_intelligence(self) -> Any:
        if self._decision_intelligence is None:
            from genesis.decisions import EngineeringDecisionIntelligence as _DI
            self._decision_intelligence = _DI(kernel=self)
        return self._decision_intelligence

    @property
    def knowledge_organizer(self) -> Any:
        if self._knowledge_organizer is None:
            from genesis.knowledge_v2 import SelfOrganizingKnowledge as _KO
            self._knowledge_organizer = _KO(kernel=self)
        return self._knowledge_organizer

    @property
    def proactive_copilot(self) -> Any:
        if self._proactive_copilot is None:
            from genesis.copilot_v2 import ProactiveCopilot as _PC
            self._proactive_copilot = _PC(kernel=self)
        return self._proactive_copilot

    @property
    def karpathy(self) -> Any:
        if not hasattr(self, '_karpathy') or self._karpathy is None:
            from genesis.agentos.karpathy import KarpathyExecutionEngine as _KE
            self._karpathy = _KE(workspace_path=".")
        return self._karpathy

    @property
    def playbooks(self) -> Any:
        if self._playbooks is None:
            from genesis.playbooks import EngineeringPlaybooks as _PB
            self._playbooks = _PB(kernel=self)
        return self._playbooks

    @property
    def app_platform(self) -> Any:
        if self._app_platform is None:
            from genesis.app_platform import GenesisAppPlatform as _AP
            self._app_platform = _AP(kernel=self)
        return self._app_platform

    @property
    def graph(self) -> GraphRegistry:
        if self._graph_registry is None:
            self._init_graph_registry()
        return self._graph_registry

    def _init_graph_registry(self):
        self._graph_registry = GraphRegistry()
        canonical = CanonicalGraph()
        self._graph_registry.set_primary(canonical)
        try:
            from genesis.graph_v2.core import UnifiedGraph as GV2UnifiedGraph
            gv2 = GV2UnifiedGraph()
            self._graph_registry.register_adapter(GraphV2Adapter(gv2))
        except Exception:
            pass
        try:
            from genesis.hypergraph import Hypergraph
            hg = Hypergraph()
            self._graph_registry.register_adapter(HypergraphAdapter(hg))
        except Exception:
            pass
        try:
            gdb = GraphDBAdapter()
            self._graph_registry.register_adapter(gdb)
        except Exception:
            pass
        try:
            from genesis.knowledge_graph import PlanetaryKnowledgeGraph
            pkg = PlanetaryKnowledgeGraph()
            self._graph_registry.register_adapter(KnowledgeGraphAdapter(pkg))
        except Exception:
            pass
        try:
            from genesis.execution_graph import build_default_execution_graph
            exg = build_default_execution_graph()
            self._graph_registry.register_adapter(ExecutionGraphAdapter(exg))
        except Exception:
            pass
        try:
            from genesis.meta.workspace import Workspace
            from genesis.meta.graph import WorkspaceDependencyGraph
            ws = Workspace()
            wdg = WorkspaceDependencyGraph(ws)
            self._graph_registry.register_adapter(MetaGraphAdapter(wdg))
        except Exception:
            pass

    @property
    def observability(self) -> ObservabilityEngine:
        if self._observability is None:
            self._observability = ObservabilityEngine(kernel=self)
        return self._observability

    @property
    def health_engine(self) -> SystemHealthEngine:
        if self._health_engine is None:
            self._health_engine = SystemHealthEngine(kernel=self)
        return self._health_engine

    @property
    def boot_engine(self) -> BootEngine:
        if self._boot_engine is None:
            self._boot_engine = BootEngine(kernel=self)
        return self._boot_engine

    @property
    def boot_report(self) -> BootReport | None:
        if self._boot_engine is None:
            return None
        return self._boot_engine.report()

    @property
    def sdk(self) -> Any:
        if self._sdk is None:
            from genesis.sdk import GenesisSDK as _SDK
            self._sdk = _SDK(kernel=self)
        return self._sdk

    def lookup(self, object_id: str) -> dict[str, Any] | None:
        cached = self._engineering.get(object_id)
        if cached:
            return cached.to_dict()
        if self._registry.get(object_id):
            inst = self._registry.get(object_id)
            return {"id": object_id, "type": "service", "name": inst.name}
        if self._agent_runtime:
            agent = self._agent_runtime.get_agent(object_id)
            if agent:
                return agent.to_dict()
            if self._agent_runtime.get_context(object_id):
                return {"id": object_id, "type": "agent_context"}
        if self._task_graph:
            node = self._task_graph.get_node(object_id)
            if node:
                return node.to_dict()
        if self._event_router._store:
            events = self._event_router._store.query(limit=1)
            for ev in events:
                if ev.id == object_id:
                    return ev.to_dict()
        if self._audit:
            results = self._audit.search(object_id, limit=1)
            if results:
                return {"id": results[0].id, "type": "audit"}
        return None

    def boot(self):
        with self._lock:
            if self.state == KernelState.RUNNING:
                return

        be = self.boot_engine

        be.add_step(BootPhase.ENVIRONMENT, "resolve_environment", lambda: None, critical=False)
        be.add_step(BootPhase.CONFIGURATION, "resolve_configuration", lambda: None, critical=False)

        be.add_step(BootPhase.CORE_KERNEL, "start_message_bus", self._bus.start)
        be.add_step(BootPhase.CORE_KERNEL, "start_scheduler", self._scheduler.start)
        be.add_step(BootPhase.CORE_KERNEL, "connect_storage",
                     lambda: self._storage.connect() if self._storage else None, critical=False)

        be.add_step(BootPhase.FABRIC, "init_agent_runtime", self._init_agent_runtime)
        be.add_step(BootPhase.FABRIC, "init_task_graph", self._init_task_graph)
        be.add_step(BootPhase.FABRIC, "init_execution_engine", self._init_execution_engine)
        be.add_step(BootPhase.FABRIC, "init_task_executor", self._init_task_executor)

        be.add_step(BootPhase.STATE, "boot_state_engine",
                     lambda: (self.state_engine.boot(), self.state_engine.set_kernel(self)))
        be.add_step(BootPhase.STATE, "boot_nervous_system", self.nervous_system.boot)
        be.add_step(BootPhase.STATE, "boot_health_engine", self.health_engine.boot)
        be.add_step(BootPhase.STATE, "boot_observability", self.observability.boot)
        be.add_step(BootPhase.STATE, "init_canonical_graph",
                     lambda: self.graph, timeout=0, critical=False)
        be.add_step(BootPhase.STATE, "register_health_collectors", self._register_health_collectors)

        be.add_step(BootPhase.ENGINEERING, "boot_observatory", self.observatory.boot, critical=False)
        be.add_step(BootPhase.ENGINEERING, "boot_explorer", self.explorer.boot, critical=False)
        be.add_step(BootPhase.ENGINEERING, "boot_planner", self.planner.boot, critical=False)
        be.add_step(BootPhase.ENGINEERING, "boot_multi_project", self.multi_project.boot, critical=False)
        be.add_step(BootPhase.ENGINEERING, "boot_live_architecture", self.live_architecture.boot, critical=False)
        be.add_step(BootPhase.ENGINEERING, "boot_visual_reasoning", self.visual_reasoning.boot, critical=False)
        be.add_step(BootPhase.ENGINEERING, "emit_state_booted",
                     lambda: self.emit("state.booted", {"domains": 0}), critical=False)
        be.add_step(BootPhase.ENGINEERING, "boot_command_center", self.command_center.boot, critical=False)

        be.add_step(BootPhase.KNOWLEDGE, "boot_knowledge_organizer", self.knowledge_organizer.boot, critical=False)

        be.add_step(BootPhase.MEMORY, "boot_memory_v2", self.memory_v2.boot, critical=False)

        be.add_step(BootPhase.REASONING, "boot_context_engine", self.context_engine.boot, critical=False)
        be.add_step(BootPhase.REASONING, "boot_insight_engine", self.insight_engine.boot, critical=False)
        be.add_step(BootPhase.REASONING, "boot_decision_intelligence", self.decision_intelligence.boot, critical=False)
        be.add_step(BootPhase.REASONING, "boot_proactive_copilot", self.proactive_copilot.boot, critical=False)

        be.add_step(BootPhase.AI, "boot_ai_engine", self.ai.boot, critical=False)
        be.add_step(BootPhase.AI, "register_automation_listener",
                     lambda: self.on_event("*", self.automation.handle_event), critical=False)

        be.add_step(BootPhase.AUTOMATION, "boot_automation", self.automation.boot, critical=False)
        be.add_step(BootPhase.AUTOMATION, "boot_workflow_engine", self.workflow_engine.boot, critical=False)

        be.add_step(BootPhase.WORKSPACE, "boot_playbooks", self.playbooks.boot, critical=False)
        be.add_step(BootPhase.WORKSPACE, "boot_agentos", self.agentos.boot, critical=False)

        be.add_step(BootPhase.APPLICATIONS, "boot_app_platform", self.app_platform.boot, critical=False)
        be.add_step(BootPhase.APPLICATIONS, "boot_sdk", self.sdk.boot, critical=False)

        be.add_step(BootPhase.VALIDATION, "emit_kernel_booted",
                     lambda: self.emit("kernel.booted", {"uptime": time.time() - self._started_at}),
                     critical=False)
        be.add_step(BootPhase.VALIDATION, "record_boot_complete",
                     lambda: self._observability and self._observability.record(
                         ActionType.BOOT, "kernel", "boot",
                         severity=ActionSeverity.INFO,
                         detail=f"Boot completed in {time.time() - self._started_at:.2f}s",
                         metadata={"phases": len(self._boot_engine.booted_phases) if self._boot_engine else 0},
                     ), critical=False)

        be.add_step(BootPhase.VALIDATION, "load_workspace_data", self._load_workspace_data, critical=False)

        be.boot()

        with self._lock:
            if be.report().boot_success:
                self.state = KernelState.RUNNING
            else:
                self.state = KernelState.DEGRADED

    def _load_workspace_data(self):
        """Load persisted workspace data on boot so web/API returns real data."""
        if self._workspace_loaded:
            return
        self._workspace_loaded = True
        try:
            from pathlib import Path
            ws_state = Path.home() / "Genesis" / "Settings" / "workspace_state.json"
            if not ws_state.exists():
                return
            import json
            state = json.loads(ws_state.read_text())
            pinned = state.get("pinned", [])

            # Set up continuous_engineering so /v1/repository returns data
            class _WatcherState:
                def __init__(self, name: str):
                    self.active = True
                    self.last_scan = ""
                    self.scan_count = 1
                    self.change_count = 0
                    self.error_count = 0

            class _ContEng:
                def states(self):
                    return {}

            ce = _ContEng()
            ws = {}
            for name in pinned:
                ws[name] = _WatcherState(name)
                # Try to load catalog
                cat_path = Path.home() / "Genesis" / "Knowledge" / name / "catalog.json"
                if cat_path.exists():
                    try:
                        catalog = json.loads(cat_path.read_text())
                        self.emit("knowledge.imported", {"project": name, "entries": len(catalog)})

                        # Register engineering object
                        from genesis.engineering.object import EngineeringObject, EngineeringObjectType
                        obj = EngineeringObject(
                            name=name,
                            object_type=EngineeringObjectType.PROJECT,
                            description=f"Project: {name}",
                            metadata={"total_files": len(catalog)},
                        )
                        self._engineering.register(obj)

                        # Seed a couple events for the timeline
                        self.emit("project.loaded", {"name": name, "catalog_size": len(catalog)})
                    except Exception:
                        pass

            ce.states = lambda _ws=ws: _ws
            self._continuous_engineering = ce
        except Exception:
            pass

    def _init_agent_runtime(self):
        mod = __import__("genesis.fabric.agents", fromlist=["AgentRuntime"])
        self._agent_runtime = mod.AgentRuntime(kernel=self)

    def _init_task_graph(self):
        mod = __import__("genesis.fabric.tasks", fromlist=["TaskGraph"])
        self._task_graph = mod.TaskGraph(kernel=self)

    def _init_execution_engine(self):
        mod = __import__("genesis.fabric.execution", fromlist=["AgentExecutionEngine"])
        self._execution_engine = mod.AgentExecutionEngine(kernel=self)

    def _init_task_executor(self):
        exec_mod = __import__("genesis.fabric.execution", fromlist=["TaskExecutor"])
        self._task_executor = exec_mod.TaskExecutor(
            kernel=self, graph=self._task_graph,
            runtime=self._agent_runtime, engine=self._execution_engine,
            poll_interval=2.0,
        )
        self._task_executor.start()

    def _register_health_collectors(self) -> None:
        he = self._health_engine
        if not he:
            return

        he.register_collector("kernel", self._collect_kernel_health)
        he.register_collector("boot", self._collect_boot_health)
        he.register_collector("event_bus", self._collect_event_bus_health)
        he.register_collector("state", self._collect_state_health)
        he.register_collector("ai", self._collect_ai_health)

    def _collect_kernel_health(self) -> HealthEntry:
        e = HealthEntry(subsystem="kernel", timestamp=time.time())
        e.add_metric(HealthDimension.AVAILABILITY, 1.0 if self.state != KernelState.SHUTDOWN else 0.0,
                     label="Kernel available")
        e.add_metric(HealthDimension.THREAD_HEALTH,
                     float(len([t for t in self._threads if t.is_alive()])),
                     max_value=max(1, len(self._threads)) if self._threads else 1.0,
                     label="Active threads")
        return e

    def _collect_boot_health(self) -> HealthEntry:
        e = HealthEntry(subsystem="boot", timestamp=time.time())
        if self._boot_engine:
            report = self._boot_engine.report()
            e.add_metric(HealthDimension.BOOT_HEALTH, float(report.phases_passed),
                         max_value=float(report.phases_total),
                         label=f"{report.phases_passed}/{report.phases_total} phases")
            e.add_metric(HealthDimension.AVAILABILITY, 1.0 if report.boot_success else 0.0,
                         label="Boot success")
        else:
            e.add_metric(HealthDimension.BOOT_HEALTH, 0.0, label="Not booted")
        return e

    def _collect_event_bus_health(self) -> HealthEntry:
        e = HealthEntry(subsystem="event_bus", timestamp=time.time())
        try:
            msg_count = len(self._bus._queues) if hasattr(self._bus, '_queues') else 0
            e.add_metric(HealthDimension.EVENT_BUS_HEALTH, 1.0, label="Bus available")
            e.add_metric(HealthDimension.QUEUE_DEPTH, float(msg_count),
                         max_value=100.0, weight=0.5, label="Bus queues")
        except Exception:
            e.add_metric(HealthDimension.EVENT_BUS_HEALTH, 0.0, label="Bus unavailable")
        return e

    def _collect_state_health(self) -> HealthEntry:
        e = HealthEntry(subsystem="state", timestamp=time.time())
        try:
            snap = self._state_engine.snapshot() if self._state_engine else {}
            domain_count = len(snap.get("domains", [])) if isinstance(snap, dict) else 0
            e.add_metric(HealthDimension.STATE_FRESHNESS,
                         1.0 if self._state_engine else 0.0,
                         label="State available")
            e.add_metric(HealthDimension.AVAILABILITY, 1.0 if self._state_engine else 0.0,
                         label="State engine")
        except Exception:
            e.add_metric(HealthDimension.STATE_FRESHNESS, 0.0, label="State error")
        return e

    def _collect_ai_health(self) -> HealthEntry:
        e = HealthEntry(subsystem="ai", timestamp=time.time())
        try:
            providers = self._ai.list_providers() if self._ai else []
            healthy = sum(1 for p in providers if p.get("health", {}).get("healthy", False))
            total = len(providers)
            e.add_metric(HealthDimension.AI_PROVIDER_HEALTH,
                         float(healthy), max_value=float(max(total, 1)),
                         label=f"{healthy}/{total} providers healthy")
        except Exception:
            e.add_metric(HealthDimension.AI_PROVIDER_HEALTH, 0.0, label="AI unavailable")
        return e

    def register_service(self, name: str, version: str = "1.0.0",
                         capabilities: list[str] | None = None) -> ServiceInstance:
        instance = self._registry.register(name, version, capabilities or [])
        self._audit.log("service.register", {"name": name, "id": instance.id})
        self.emit("service.registered", {"name": name, "id": instance.id}, origin="fabric")
        if self._storage and self._storage.connected:
            self._storage.store_service({
                "id": instance.id, "name": instance.name,
                "version": instance.version,
                "capabilities": instance.capabilities,
                "status": instance.status,
                "registered_at": instance.registered_at,
                "last_heartbeat": instance.last_heartbeat,
                "metadata": instance.metadata,
            })
        eng_obj = EngineeringObject(
            id=instance.id,
            object_type=EngineeringObjectType.SERVICE,
            name=name,
            description=f"Service {name} v{version}",
            tags=capabilities or [],
            metadata={"version": version, "instance_id": instance.instance_id if hasattr(instance, 'instance_id') else ""},
        )
        self._engineering.register(eng_obj)
        return instance

    def unregister_service(self, instance_id: str) -> bool:
        result = self._registry.unregister(instance_id)
        if result:
            self._audit.log("service.unregister", {"id": instance_id})
            self.emit("service.unregistered", {"id": instance_id}, origin="fabric")
            if self._storage and self._storage.connected:
                self._storage.delete_service(instance_id)
        return result

    def send(self, topic: str, body: Any,
             correlation_id: str | None = None,
             source: str | None = None) -> Message:
        ctx = Context(correlation_id=correlation_id or generate_id("corr", 12))
        msg = self._bus.publish(topic, body, ctx, source)
        self._metrics.record("fabric.messages.sent", 1.0)
        self.emit("message.sent", {"topic": topic, "id": msg.id}, origin="fabric")
        return msg

    def subscribe(self, topic: str, handler: Callable):
        self._bus.subscribe(topic, handler)

    def on(self, event: str, handler: Callable):
        self._hooks[event].append(handler)

    def _emit(self, event: str, data: dict[str, Any]):
        for handler in self._hooks.get(event, []):
            try:
                handler(data)
            except Exception:
                pass

    def emit(self, event_type: str, payload: dict[str, Any] | None = None,
             origin: str = "fabric", correlation_id: str = "", causation_id: str = "",
             session_id: str = "", repository_id: str = "",
             priority: EventPriority = EventPriority.NORMAL,
             severity: EventSeverity = EventSeverity.INFO,
             tags: list[str] | None = None, confidence: float = 1.0) -> EngineeringEvent:
        ev = self._event_router.emit_raw(
            event_type=event_type, payload=payload, origin=origin or "fabric",
            correlation_id=correlation_id, causation_id=causation_id,
            session_id=session_id, repository_id=repository_id,
            priority=priority, severity=severity, tags=tags, confidence=confidence,
        )
        if self._storage and self._storage.connected:
            try:
                self._storage.store_event(ev)
            except Exception:
                pass
        return ev

    def on_event(self, event_type: str, handler: Callable[[EngineeringEvent], None],
                 filter_fn: Callable[[EngineeringEvent], bool] | None = None):
        self._event_router.subscribe(event_type, handler, filter_fn)

    def query_events(self, **kwargs) -> list[EngineeringEvent]:
        return self._event_router._store.query(**kwargs)

    def begin_session(self, session_type: str = "engineering",
                      metadata: dict[str, Any] | None = None) -> Context:
        ctx = Context(
            correlation_id=generate_id("corr", 12),
            transaction_id=generate_id("txn", 12),
            session_id=generate_id("sess", 12),
            metadata=metadata or {},
        )
        ctx.set("session_type", session_type)
        ctx.set("started_at", time.time())
        with self._lock:
            self._contexts[ctx.session_id] = ctx
        entry = self._audit.log("session.begin", {"session_id": ctx.session_id, "type": session_type})
        self.emit("session.begun", {"session_id": ctx.session_id, "type": session_type}, origin="fabric")
        if self._storage and self._storage.connected:
            self._storage.store_audit_entry({
                "id": entry.id, "action": entry.action,
                "actor": entry.actor, "resource": entry.resource,
                "detail": entry.detail, "timestamp": entry.timestamp,
                "severity": entry.severity,
                "correlation_id": entry.correlation_id,
                "session_id": entry.session_id,
            })
        eng_obj = EngineeringObject(
            id=ctx.session_id,
            object_type=EngineeringObjectType.SESSION,
            name=f"{session_type} session",
            description=f"Engineering session of type {session_type}",
            tags=[session_type],
            metadata=metadata or {},
        )
        self._engineering.register(eng_obj)
        return ctx

    def end_session(self, session_id: str):
        with self._lock:
            self._contexts.pop(session_id, None)
        entry = self._audit.log("session.end", {"session_id": session_id})
        self.emit("session.ended", {"session_id": session_id}, origin="fabric")
        if self._storage and self._storage.connected:
            self._storage.store_audit_entry({
                "id": entry.id, "action": entry.action,
                "actor": entry.actor, "resource": entry.resource,
                "detail": entry.detail, "timestamp": entry.timestamp,
                "severity": entry.severity,
                "correlation_id": entry.correlation_id,
                "session_id": entry.session_id,
            })

    def get_context(self, session_id: str) -> Context | None:
        return self._contexts.get(session_id)

    def schedule(self, interval_secs: float, callback: Callable,
                 name: str = "") -> str:
        task = self._scheduler.schedule(interval_secs, callback, name)
        entry = self._audit.log("task.scheduled", {"name": name, "id": task.id})
        if self._storage and self._storage.connected:
            self._storage.store_audit_entry({
                "id": entry.id, "action": entry.action,
                "actor": entry.actor, "resource": entry.resource,
                "detail": entry.detail, "timestamp": entry.timestamp,
                "severity": entry.severity,
                "correlation_id": entry.correlation_id,
                "session_id": entry.session_id,
            })
        return task.id

    def health(self) -> ServiceHealth:
        uptime = time.time() - self._started_at
        with self._lock:
            return ServiceHealth(
                status=self.state.value,
                uptime_seconds=uptime,
                services_count=self._registry.count(),
                messages_sent=self._bus.message_count(),
                active_sessions=len(self._contexts),
                threads=len(self._threads),
            )

    def stats(self) -> KernelStats:
        h = self.health()
        stats = KernelStats(
            services=h.services_count,
            messages_sent=self._bus.message_count(),
            active_sessions=h.active_sessions,
            uptime_seconds=h.uptime_seconds,
            threads=h.threads,
            state=h.status,
            events_delivered=self._event_router.stats()["delivered"],
            event_store_count=self._event_router._store.count(),
        )
        if self._task_executor:
            es = self._task_executor.stats
            stats.executor_running = es["running"]
            stats.executor_executions = es["execution_count"]
            stats.executor_failed = es["failed_count"]
        return stats

    def search(self, query: str, sources: str = "all", limit: int = 20) -> list[dict[str, Any]]:
        """Unified engineering search across all subsystems."""
        q = query.lower().strip()
        if not q:
            return []
        results: list[dict[str, Any]] = []
        allowed = sources.split(",") if sources != "all" else []

        def active(src: str) -> bool:
            return sources == "all" or src in allowed

        if active("registry") or active("engineering"):
            for obj in self._engineering.search(q, limit=limit // 2):
                results.append({
                    "type": "engineering_object",
                    "label": f"[Engineering] {obj.name} ({obj.object_type})",
                    "relevance": 0.9,
                    "id": obj.id,
                })
        if active("knowledge"):
            ke = self._knowledge
            if ke and hasattr(ke, 'search'):
                for item in ke.search(q, limit=limit // 2):
                    label = item.get("content", str(item))[:100] if isinstance(item, dict) else str(item)[:100]
                    results.append({
                        "type": "knowledge",
                        "label": f"[Knowledge] {label}",
                        "relevance": 0.85,
                    })
        if active("events"):
            for ev in self.query_events(limit=limit // 2):
                if q in ev.type.lower() or q in ev.origin.lower() or q in str(ev.payload).lower():
                    results.append({"type": "event", "label": f"[Event] {ev.type} ({ev.origin})", "relevance": 0.7, "id": ev.id})
        if active("audit"):
            for e in self._audit.query(limit=limit // 2):
                if q in e.action.lower() or q in e.actor.lower():
                    results.append({"type": "audit", "label": f"[Audit] {e.action} by {e.actor}", "relevance": 0.6, "id": e.id})
        if active("timeline"):
            tl = self._timeline
            if tl and hasattr(tl, 'query'):
                for entry in tl.query(limit=limit // 2):
                    label = entry.get("type", entry.get("event_type", "?"))
                    if q in label.lower():
                        results.append({"type": "timeline", "label": f"[Timeline] {label}", "relevance": 0.75})
        if active("providers") or active("ai"):
            ai = self._ai
            if ai and hasattr(ai, 'list_providers'):
                for p in ai.list_providers():
                    if q in p["id"].lower():
                        results.append({"type": "provider", "label": f"[AI Provider] {p['id']}", "relevance": 0.8})

        results.sort(key=lambda r: -r["relevance"])
        return results[:limit]

    def shutdown(self):
        self.state = KernelState.SHUTDOWN
        if self._boot_engine:
            self._boot_engine.shutdown()
        if self._task_executor:
            self._task_executor.stop()
        self._scheduler.stop()
        self._bus.stop()
        entry = self._audit.log("kernel.shutdown", {"uptime": time.time() - self._started_at})
        if self._storage and self._storage.connected:
            self._storage.store_audit_entry({
                "id": entry.id, "action": entry.action,
                "actor": entry.actor, "resource": entry.resource,
                "detail": entry.detail, "timestamp": entry.timestamp,
                "severity": entry.severity,
                "correlation_id": entry.correlation_id,
                "session_id": entry.session_id,
            })
            self._storage.disconnect()
        self.emit("kernel.shutdown", {"uptime": time.time() - self._started_at}, origin="fabric")
