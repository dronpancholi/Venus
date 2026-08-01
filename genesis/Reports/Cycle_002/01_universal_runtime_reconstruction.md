# PROJECT NEMESIS — PHASE II: Mission 5

## Universal Runtime Reconstruction

**Date**: 2026-06-30
**Cycle**: 002

---

## Executive Summary

The Genesis codebase contains **7 distinct execution/runtime systems** with overlapping responsibilities and fragmented ownership. No single system owns "execution" — the capability is scattered across `runtime/executor.py`, `execution/`, `execution_graph.py`, `os/runtime.py`, `kernel/`, `fabric/`, and `autonomous/cycle.py`. This report performs complete runtime archaeology, identifies every execution object, traces the runtime lifecycle, and proposes a Universal Runtime Model.

---

## 1. Runtime Archaeology — Every Execution Object

### 1.1 System A: `runtime/executor.py` (266 lines)

| Aspect | Value |
|---|---|
| **Class** | `ExecutionEngine` |
| **Created by** | `platform.py` boot() Phase 2 |
| **Owned by** | `VenusPlatform.executor` |
| **Dependencies** | EventBus, HistoryStore |
| **Registered in DI** | Yes (as ExecutionEngine) |
| **Consumers** | None — created but never executed by any consumer |
| **Purpose** | DAG workflow execution with event emission |
| **Lifecycle** | register_workflow → plan → execute |
| **State** | In-memory only (history persists through HistoryStore) |
| **Shutdown** | None |
| **Model** | Task → Workflow (DAG) → ExecutionEngine (sequential executor) |

**Objects**:
- `Task` — single executable unit with handler, dependencies, status
- `Workflow` — named DAG of tasks with top_sort
- `ExecutionEngine` — registers workflows, plans, executes synchronously
- `TaskStatus` — PENDING, RUNNING, COMPLETED, FAILED, SKIPPED, BLOCKED

### 1.2 System B: `execution/` package (5 sub-engines, ~568 lines total)

| Aspect | Value |
|---|---|
| **Class** | `ExecutionEngine` (`execution/engine.py`) |
| **Created by** | `platform.py` boot() Phase 7 (as ExecutionEngineV2) |
| **Owned by** | `VenusPlatform.execution_engine` |
| **Dependencies** | None (no-arg constructor) |
| **Registered in DI** | Yes (as `execution.engine.ExecutionEngine`) |
| **Consumers** | EngineeringOrchestrator |
| **Purpose** | Unified execution model dispatching to 5 sub-engines |
| **Lifecycle** | execute(model_type, payload) → dispatches to sub-engine |
| **State** | In-memory history |
| **Shutdown** | None |

**Sub-engines**:

| Sub-engine | File | Lines | Model |
|---|---|---|---|
| WorkflowEngine | `execution/workflow.py` | 128 | WorkflowDAG → topological sort → sequential node execution |
| TaskExecutor | `execution/tasks.py` | 139 | Priority queue → execute with retry |
| ActorEngine | `execution/actors.py` | 112 | Actor model with message passing |
| PipelineEngine | `execution/pipeline.py` | 84 | Sequential pipeline stages with retry |
| RetryPolicy | `execution/retry.py` | 54 | Retry + compensation |
| JobManager | `execution/jobs.py` | — | Job management |
| CompensationEngine | `execution/retry.py` | — | Compensation actions |

**This system subsumes System A's model** (WorkflowEngine duplicates Workflow, TaskExecutor duplicates Task).

### 1.3 System C: `execution_graph.py` (420 lines)

| Aspect | Value |
|---|---|
| **Class** | `ExecutionGraph`, `ExecutionEngine` (2nd), `ExecutionGraphMonitor` |
| **Created by** | `platform.py` boot() Phase 8 |
| **Owned by** | `VenusPlatform.exec_graph`, `exec_graph_engine`, `exec_graph_monitor` |
| **Dependencies** | None (graph built by `build_default_execution_graph()`) |
| **Registered in DI** | Yes (ExecGraphEngine, ExecutionGraphMonitor) |
| **Consumers** | None — monitor sits idle |
| **Purpose** | Meta-execution graph modeling every platform phase |
| **Lifecycle** | topological_order → execute each node → emit events → complete |
| **Shutdown** | None |
| **Model** | ExecutionGraph (DAG of ExecutionNodes) → ExecutionEngine (walks it) → ExecutionTrace |

**Nodes**: boot, runtime, scheduler, planner, brain, memory, execution, compiler, verification, graph, economics, learning, evolution, shutdown

**This is a meta-model of execution** — it models what the platform SHOULD do, not what it DOES. The ExecutionEngine.execute() just iterates through nodes with `time.sleep(0)` — it's a simulation, not real execution.

### 1.4 System D: `os/runtime.py` (499 lines) + `os/` package (7 sub-systems)

| Aspect | Value |
|---|---|
| **Class** | `AutonomousRuntime` |
| **Created by** | NOT created by platform.py (unused) |
| **Owned by** | No one (orphaned) |
| **Dependencies** | 10+ OS sub-systems, optional EngineeringBrain |
| **Consumers** | None |
| **Purpose** | Persistent self-healing daemon runtime with watchdog, health checks, ticks |
| **Lifecycle** | INITIALIZING → STARTING → RUNNING → DEGRADED → STOPPING → STOPPED |
| **State** | Disk-persisted via JSON |
| **Shutdown** | Graceful with timeout |

**Sub-systems**:

| Sub-system | File | Lines | Role |
|---|---|---|---|
| PersistentScheduler | `os/scheduler.py` | 199 | Time-based + event-based persistent job scheduler |
| PersistentPlanner | `os/planner.py` | 198 | Goal decomposition into plan steps |
| PersistentTaskGraph | `os/task_graph.py` | 197 | DAG tasks with persistence |
| DistributedQueue | `os/queue.py` | — | Queue with ack/nack |
| AgentRuntime | `os/agent_runtime.py` | — | Agent process management |
| ResourceAllocator | `os/resource_allocator.py` | — | Resource reservation |
| MemoryManager | `os/memory_manager.py` | — | Memory tracking |
| CheckpointManager | `os/checkpoint.py` | — | Snapshot management |
| RecoveryManager | `os/recovery.py` | — | Recovery actions |
| ObservationManager | `os/observation.py` | — | Runtime observation recording |

**This is the most complete runtime system** — it has health checks, tick loop, checkpointing, recovery, and persistence. But it's **completely orphaned** — never created or consumed.

### 1.5 System E: `kernel/` package (16 files)

| Aspect | Value |
|---|---|
| **Class** | `UniversalKernel` (facade), `ExecutionManager`, `TaskScheduler`, etc. |
| **Created by** | `platform.py` boot() Phase 5 |
| **Owned by** | `VenusPlatform.kernel` |
| **Dependencies** | None (all sub-systems use no-arg constructors) |
| **Registered in DI** | Yes |
| **Consumers** | None |
| **Purpose** | Foundational execution layer — process, task, memory, storage, IPC, events, plugins, DI, resources, execution, health, security |
| **Lifecycle** | boot() → publish "kernel.boot" event |
| **Shutdown** | shutdown() → publish "kernel.shutdown" event |

**Sub-managers**:
- ProcessManager — process lifecycle
- TaskScheduler — task scheduling
- MemoryManager — memory blocks
- StorageManager — storage volumes
- CheckpointManager — checkpoint plans
- RecoveryManager — recovery plans
- EventRouter — internal event routing (DUPLICATES EventBus)
- IPC — inter-process communication
- PluginLoader — plugin management (DUPLICATES PluginManager)
- DIKernel — DI container (DUPLICATES ServiceProvider)
- ResourceManager — resource reservations
- ExecutionManager — multi-step execution plans
- HealthManager — health probes
- SecurityManager — security enforcement
- CapabilityLoader — capability loading

**This is a complete OS stack** — it duplicates EventBus, PluginManager, ServiceProvider, and every execution model.

### 1.6 System F: `fabric/kernel.py` (193 lines) + `fabric/` package (11 files)

| Aspect | Value |
|---|---|
| **Class** | `FabricKernel` (singleton), `DistributedScheduler` |
| **Created by** | `platform.py` boot() Phase 7 (`FabricKernel.instance()`) |
| **Owned by** | `VenusPlatform.fabric` |
| **Dependencies** | None |
| **Registered in DI** | Yes |
| **Consumers** | EngineeringOrchestrator |
| **Purpose** | Central fabric — service registry, message bus, scheduler, policy, audit, metrics |
| **Lifecycle** | BOOTING → RUNNING → DEGRADED → SHUTDOWN |
| **Shutdown** | None |

**Sub-systems**:
- MessageBus — pub/sub (DUPLICATES EventBus)
- ServiceRegistry — service discovery
- DistributedScheduler — job scheduling
- PolicyEngine — contract policies
- FabricMetrics — metrics collection
- AuditLog — audit trail

### 1.7 System G: `autonomous/cycle.py` + `autonomous/orchestrator.py` (320 lines total)

| Aspect | Value |
|---|---|
| **Classes** | `AutonomousEngine`, `EngineeringOrchestrator` |
| **Created by** | `platform.py` boot() Phase 7 (Orchestrator), AutonomousEngine created inside Orchestrator |
| **Owned by** | `VenusPlatform.orchestrator` |
| **Dependencies** | Orchestrator depends on FabricKernel, UnifiedGraph, Database, ExecutionEngine |
| **Consumers** | None |
| **Purpose** | 22-stage autonomous engineering cycle (Observe → ... → Repeat) |
| **Lifecycle** | run() → iterate CYCLE_ORDER → register handlers → run_continuous |
| **Shutdown** | stop() |

**Stages**: 22 canonical stages + 8 internal stages = 30 stages.
**Model**: AutonomousEngine (stage→handler registry) → CycleRun (result container)

**This is the highest-level execution system** — it orchestrates all others. But it's a stub: all handlers are no-ops that just return `{"done": True}`.

---

## 2. Duplication Matrix

### 2.1 Task/Workflow Models (3+ implementations)

| Concept | runtime/ | execution/ | os/ | kernel/ | execution_graph/ |
|---|---|---|---|---|---|
| Task | Task | Task | Task | TaskInfo | ExecutionNode |
| Workflow | Workflow | WorkflowDAG | PersistentTaskGraph | ExecutionManager | ExecutionGraph |
| Executor | ExecutionEngine | WorkflowEngine/TaskExecutor | AutonomousRuntime | TaskScheduler | Graph ExecutionEngine |
| Scheduler | — | — | PersistentScheduler | TaskScheduler | — |
| Status | TaskStatus | WorkflowStatus/TaskStatus | task.status | TaskState | NodeStatus |
| DAG | dependencies | dependencies | dependencies | steps | edges |
| Topo sort | Yes | Yes | Yes | No | Yes |
| Persistence | HistoryStore | None | JSON files | None | None |
| Events | EventBus | None | Custom | EventRouter | Custom listeners |

### 2.2 Service/Runtime Models (4+ implementations)

| Concept | platform.py | os/ | kernel/ | fabric/ |
|---|---|---|---|---|
| Bootstrap | bootstrap() | INITIALIZING | boot() | BOOTING |
| Run | boot() | RUNNING boot() | — | RUNNING |
| Shutdown | shutdown() | STOPPING | shutdown() | SHUTDOWN |
| Health | None | Health check loop | HealthManager | Health probes |
| Recovery | None | RecoveryManager | RecoveryManager | — |
| State | _booted bool | RuntimeStatus | — | KernelState |
| DI | ServiceProvider | None | DIKernel | — |
| Events | EventBus | Observations | EventRouter | MessageBus |

---

## 3. Runtime Lifecycle (Actual vs Declared)

### 3.1 What Actually Happens on Boot

```
Python interpreter
  ↓
Module imports (platform.py) → 50+ modules, 7 deprecation warnings
  ↓
VenusPlatform.__init__() → declares 50 attributes
  ↓
bootstrap() → ServiceProvider + 6 stores + EventBus
  ↓
boot() core services → 15 objects (Compiler, Graph, Executor, Memory, Brain, VRIP...)
  ↓
boot() GENESIS-VIII → 22 objects (16 memories, physics, OS, civ, evolution...)
  ↓
boot() GENESIS-IX → 7 objects (platform_v2, brain_v4, UMS, hypergraph...)
  ↓
boot() GENESIS-X → 2 objects (UCOS, kernel)
  ↓
boot() GENESIS-XI → 2 objects (MetaCompiler, UED)
  ↓
boot() GENESIS-XII → 4 objects (Fabric, UnifiedGraph, ExecEngineV2, Orchestrator)
  ↓
boot() Ω³ → 12 objects (MetaModel, ExecGraph, Economics, Planner, Reasoning, ...)
  ↓
register shutdown hook → platform.shutdown
  ↓
emit "platform.boot.completed"
```

### 3.2 What the Execution Graph SAYS Should Happen

```
boot → runtime → scheduler → planner → brain → memory → execution →
compiler → verification → graph → economics → learning → evolution → shutdown
```

**Reality**: boot() creates everything sequentially. No scheduler, no planner invocation, no phase transitions. The execution graph is aspirational.

### 3.3 What the Autonomous Cycle SAYS Should Happen

```
Observe → Acquire → Understand → Represent → Reason → Predict → Plan →
Research → Experiment → Simulate → Validate → Implement → Compile → Test →
Benchmark → Secure → Deploy → Monitor → Reflect → Learn → Remember →
Improve → Repeat
```

**Reality**: All handlers are stubs returning `{"done": True}`. Nothing happens.

### 3.4 What Actually Runs

Only `platform.py boot()` actually executes. Everything else is:
- **Dead code**: never invoked (os/runtime, kernel/ExecutionManager)
- **Stubs**: handlers that return trivial values (AutonomousEngine)
- **Simulation**: execution graph walker that records elapsed = sleep(0) (execution_graph)

---

## 4. Universal Runtime Model

### 4.1 Design Principles

1. **One runtime, one executor** — all execution models are specializations of a single canonical runtime
2. **Phases are real state machines** — not just comments in boot()
3. **Every phase has entry/exit conditions** — not just sequential object creation
4. **Health is first-class** — observable, recoverable, reportable
5. **Persistence is opt-in** — not all state needs to survive restarts
6. **Events are the nervous system** — all state transitions emit events
7. **Execution is observable** — traces, metrics, history always available

### 4.2 Universal Runtime State Machine

```
                    ┌─────────────────────────────────────┐
                    │              BOOT                    │
                    │  entry: validate_config, init_di    │
                    │  exit:  event_bus_ready, stores_up  │
                    └────────────┬────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────┐
                    │         INITIALIZING                 │
                    │  entry: create_core_services         │
                    │  exit:  services_registered          │
                    └────────────┬────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────┐
                    │           STARTING                   │
                    │  entry: wire_dependencies            │
                    │  exit:  all_services_initialized     │
                    └────────────┬────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────┐
                    │           RUNNING                    │◄──────────────────────┐
                    │  entry: start_tick_loop              │                       │
                    │  exit:  shutdown_requested           │                       │
                    │  do:    tick → process → checkpoint  │                       │
                    └────────────┬────────────────────────┘                       │
                                 │                                                │
                    ┌────────────▼────────────────────────┐                       │
                    │           DEGRADED                   │────► recovery ───────┘
                    │  entry: >50% components unhealthy    │
                    │  do:    auto_recovery                │
                    └────────────┬────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────┐
                    │          STOPPING                    │
                    │  entry: drain_queue, flush_stores    │
                    │  exit:  all_components_stopped       │
                    └────────────┬────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────┐
                    │           STOPPED                    │
                    │  entry: save_final_checkpoint        │
                    │  exit:  (restart or terminate)       │
                    └─────────────────────────────────────┘
```

### 4.3 Runtime Phase Contracts

| Phase | Entry Condition | Exit Condition | Failure Mode |
|---|---|---|---|
| BOOT | interpreter started | DI container + stores ready | Cannot start — config error |
| INITIALIZING | stores + event bus ready | All core services registered | Partial initialization — degrade |
| STARTING | services registered | All wiring complete | Wiring failure — retry |
| RUNNING | wiring complete | Shutdown signal received | Component failure — degrade |
| DEGRADED | >50% health failures | Health restored or stop | Unrecoverable — force stop |
| STOPPING | stop signal | All stores flushed | Force shutdown after timeout |
| STOPPED | stores flushed | Final checkpoint saved | Data loss — corruption |

### 4.4 Execution Models (Unified)

Instead of 7 competing execution models, the Universal Runtime defines:

```
ExecutionModel (abstract)
  ├── TaskModel       — single unit of work with retry
  ├── WorkflowModel   — DAG of tasks with topological execution
  ├── PipelineModel   — sequential stages with retry
  ├── ActorModel      — message-passing actors
  ├── ScheduleModel   — time/event-triggered jobs
  └── CycleModel      — autonomous engineering cycles
```

Each model implements:
- `execute(context) → Result`
- `validate() → Validation`
- `estimate_cost() → float`
- `to_trace() → ExecutionTrace`

### 4.5 Health Model

```python
@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus  # HEALTHY, DEGRADED, UNHEALTHY, DISABLED
    last_ok: float
    last_error: str
    error_count: int
    recovery_count: int
    check: Callable[[], bool]  # health check function

class HealthRegistry:
    def register(self, name: str, check: Callable, interval: float)
    def check_all(self) -> dict[str, ComponentHealth]
    def on_unhealthy(self, name: str, handler: Callable)
    def on_recovered(self, name: str, handler: Callable)
```

### 4.6 Recovery Model

```python
@dataclass
class RecoveryStrategy:
    name: str
    condition: Callable[[Exception], bool]
    action: Callable[[], bool]  # returns True if recovered
    max_attempts: int = 3
    backoff: float = 1.0  # seconds

class RecoveryManager:
    def register(self, strategy: RecoveryStrategy)
    def attempt(self, context: str, error: Exception) -> bool
    def history(self) -> list[RecoveryAttempt]
```

### 4.7 Observability

```python
@dataclass
class RuntimeObservation:
    phase: str
    event: str
    value: float
    tags: dict
    timestamp: float

class ObservationCollector:
    def record(self, observation: RuntimeObservation)
    def query(self, phase: str = "", event: str = "") -> list[RuntimeObservation]
    def metrics(self) -> dict[str, float]

@dataclass
class ExecutionTrace:
    trace_id: str
    model_type: str
    started_at: float
    completed_at: float
    events: list[TraceEvent]
    result: Any
    error: str = ""
```

### 4.8 Ownership Boundaries

| Responsibility | Canonical Owner | Rationale |
|---|---|---|
| Runtime state machine | `runtime/` | Core lifecycle management |
| Task execution | `runtime/` | Single unit of work |
| Workflow execution | `runtime/` | DAG orchestration |
| Pipeline execution | `runtime/` | Sequential processing |
| Actor execution | `runtime/` | Message-passing concurrency |
| Health monitoring | `runtime/health.py` | Component health tracking |
| Recovery | `runtime/recovery.py` | Failure recovery |
| Observability | `runtime/observability.py` | Metrics and tracing |
| Scheduling | `runtime/scheduler.py` | Time/event-based triggers |
| Cycle orchestration | `autonomous/` | Autonomous engineering loop |
| Service registry | `di/` | Service discovery (already exists) |
| Event routing | `events/` | Pub/sub (already exists) |

### 4.9 Migration Path

| Step | Action | Risk |
|---|---|---|
| 1 | Move `runtime/executor.py` → `runtime/core.py` (canonical runtime) | Low — no consumers |
| 2 | Deprecate `execution/` package | Low — no consumers |
| 3 | Deprecate `execution_graph.py` execution simulation | Low — no consumers |
| 4 | Deprecate `os/runtime.py` + `os/` package | Low — orphaned |
| 5 | Deprecate `kernel/` execution_manager + task_scheduler | Low — orphaned |
| 6 | Add HealthRegistry to DI container | Medium — new API |
| 7 | Add ObservationCollector to runtime | Medium — new API |
| 8 | Move cycle orchestration into AutonomousEngine | High — stub handlers need implementation |

---

## 5. Remaining Technical Debt

| Debt | Location | Impact |
|---|---|---|
| 7 competing execution systems | runtime/, execution/, execution_graph, os/, kernel/, fabric/, autonomous/ | Cannot reason about execution |
| Orphaned AutonomousRuntime | os/runtime.py | 499 lines of dead code |
| Orchestrator stubs | autonomous/orchestrator.py | 30 stages, all return {"done": True} |
| No health checks on boot | platform.py | 50+ services, 0 health checks |
| No runtime state machine | platform.py | Single _booted boolean |
| Execution graph is simulation | execution_graph.py | Walks nodes without running them |

---

## 6. Engineering Decisions

1. **The Universal Runtime should live in `runtime/`** — this package has the cleanest model (Task → Workflow → ExecutionEngine with EventBus integration). It needs to be extended with health, recovery, scheduling, and observability — not replaced.

2. **execution/ package should be deprecated** — it's a parallel universe that duplicates everything in runtime/ with no consumers.

3. **execution_graph.py should be merged into runtime/** — the ExecutionNode/ExecutionEdge model is useful for meta-execution modeling, but the ExecutionEngine there should be removed (it's a simulation, not real execution).

4. **os/runtime.py** should be marked as deprecated — it's the most complete runtime but it's orphaned, and its concepts (health, ticks, checkpoints, recovery) should be migrated into runtime/ rather than maintained separately.

5. **kernel/ and fabric/ execution sub-systems** should be deprecated — they duplicate existing capabilities without adding value.

---

**End of Mission 5: Universal Runtime Reconstruction.**
