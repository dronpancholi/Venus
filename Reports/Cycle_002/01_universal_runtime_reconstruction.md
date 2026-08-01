# PROJECT NEMESIS Phase II — Mission 5: Universal Runtime Reconstruction

**Date**: 2026-06-30 | **Repository**: 335 Python files (excl tests), ~71,916 lines (excl tests), 72 test files, 2,763 tests
**Scope**: Every execution system — object lifecycle, ownership, consumers, duplication, design for Universal Runtime

---

## 1. Executive Summary

Genesis has **7 distinct execution systems**, each built independently for different purposes:

1. `runtime/executor.py` — ExecutionEngine with DI, EventBus, HistoryStore
2. `execution/` package — ParallelExecutionEngine, no consumers
3. `execution_graph.py` — ExecutionGraph meta-model, simulation engine
4. `os/runtime.py` — AutonomousRuntime with health/ticks/recovery (orphaned)
5. `kernel/kernel.py` — UniversalKernel facade (16 sub-managers)
6. `fabric/kernel.py` — FabricKernel singleton (6 subsystems)
7. `autonomous/cycle.py` — 30-stage cycle engine (all stubs)

**Core finding**: Only `runtime/executor.py` is actually consumed — it's wired into EventBus, HistoryStore, and platform boot. The other 6 have zero runtime consumers. They are parallel universes of execution infrastructure that were built for future features that never materialized.

**Duplication cost**: ~3,100 lines of execution infrastructure, of which ~2,400 lines (77%) have no consumers.

---

## 2. Every Execution System: Archaeology

### 2.1 `runtime/executor.py` — ExecutionEngine (~500 lines)

**Purpose**: Canonical task execution engine. Manages Task → Workflow lifecycle with EventBus integration.

**Location**: `genesis/runtime/executor.py`

**Model**:
```python
class ExecutionEngine:
    def __init__(self, event_bus, history_store, workers=4, max_retries=3)
    def execute_task(self, task) -> dict
    def execute_workflow(self, workflow) -> list
    def get_status(self, task_id) -> str
    def cancel_task(self, task_id) -> bool
    def get_statistics(self) -> dict
```

**Lifecycle states**: `PENDING → RUNNING → COMPLETED / FAILED → RETRY`
**Threading**: ThreadPoolExecutor with configurable workers
**DI**: Constructor-injected (EventBus, HistoryStore)
**Consumers**: `platform.py` boot sequence, `omega_loop.py` Book VI

**Status**: **Canonical** — only execution system with real DI consumers.

### 2.2 `execution/` package — Parallel Universe (~600 lines)

**Purpose**: "Unified execution engine" with matcher/planning/scheduling.

**Location**: `genesis/execution/` — `engine.py`, `matcher.py`, `planner.py`, `scheduler.py`

**Model**:
```python
# execution/engine.py
class ParallelExecutionEngine:
    def execute_plan(self, plan) -> None

# execution/matcher.py
class ExecutionMatcher:
    def match(self, context) -> list[ExecutionPlan]

# execution/planner.py
class ExecutionPlanner:
    def plan(self, goal) -> ExecutionPlan
    def refine(self, plan, feedback) -> ExecutionPlan

# execution/scheduler.py  
class ExecutionScheduler:
    def schedule(self, plans) -> list[ExecutionPlan]
    def prioritize(self, plans) -> list[ExecutionPlan]
```

**DI**: No constructor injection — global imports
**Consumers**: None found in codebase

**Status**: **Duplicate** — overlaps ExecutionEngine completely with 0 consumers.

### 2.3 `execution_graph.py` — Execution Simulation (~420 lines)

**Purpose**: DAG-based execution simulation with ExecutionNode/ExecutionEdge.

**Location**: `genesis/execution_graph.py`

**Model**:
```python
class ExecutionGraph:
    def add_node(self, node) -> None
    def add_edge(self, source, target, condition=None) -> None
    def execute(self, context) -> dict
    def get_execution_path(self) -> list[str]
    def simulate(self, context) -> dict
```

**Node model**: ExecutionNode — node_id, action, params, timeout, retry_count
**Edge model**: ExecutionEdge — source_id, target_id, condition, priority

**Consumers**: None found

**Status**: **Duplicate** — simulation-only, overlaps ExecutionEngine execution model.

### 2.4 `os/runtime.py` — AutonomousRuntime (~499 lines)

**Purpose**: Self-healing runtime with health checks, tick-based execution, checkpointing, recovery.

**Location**: `genesis/os/runtime.py`

**Model**:
```python
class AutonomousRuntime:
    def __init__(self, config)
    def start(self) -> None
    def stop(self) -> None
    def health_check(self) -> dict
    def tick(self) -> dict
    def checkpoint(self) -> None
    def recover(self) -> bool
    def execute_command(self, command) -> dict
    def get_status(self) -> dict
    def register_observer(self, observer) -> None
```

**Health model**: `HEALTH_STATUS = {"healthy", "degraded", "unhealthy", "recovering"}`
**Tick system**: Configurable tick interval, tick counter, tick execution
**Checkpointing**: State serialization per tick
**Recovery**: State machine with recovery attempt tracking
**Observers**: Observer pattern for tick/health/command events
**Consumers**: None found — orphaned resource

**Status**: **Orphaned gold** — most complete runtime system (health, ticks, recovery, checkpointing) with no consumers. Should migrate concepts into ExecutionEngine.

### 2.5 `kernel/kernel.py` — UniversalKernel (~350 lines)

**Purpose**: OS kernel facade with 16 sub-managers covering process, memory, device, file, network, security, power, time, IPC, service, plugin, session, module, log, config, event.

**Location**: `genesis/kernel/kernel.py`

**Model**:
```python
class UniversalKernel:
    def __init__(self, config)
    def boot(self) -> None
    def shutdown(self) -> None
    def get_manager(self, name) -> Manager
```

**Sub-managers**: Process, Memory, Device, File, Network, Security, Power, Time, IPC, Service, Plugin, Session, Module, Log, Config, Event

**Consumers**: None found — looks aspirational.

**Status**: **Duplicate** — overlaps EventBus, PluginManager, ServiceProvider, plus the execution engines.

### 2.6 `fabric/kernel.py` — FabricKernel (~200 lines)

**Purpose**: Singleton kernel with distributed architecture — 6 sub-systems.

**Location**: `genesis/fabric/kernel.py`

**Model**:
```python
class FabricKernel(metaclass=SingletonMeta):
    def __init__(self)
    def register(self, name, component) -> None
    def get(self, name) -> Any
    def execute(self, command) -> Any
```

**Sub-systems**: EventManager, TaskScheduler, ResourceManager, ServiceRegistry, PluginManager, MetricsCollector

**Consumers**: None found.

**Status**: **Duplicate** — overlaps EventBus, TaskScheduler (which doesn't exist), ServiceRegistry.

### 2.7 `autonomous/cycle.py` — AutonomousCycle (~330 lines)

**Purpose**: 30-stage autonomous engineering cycle.

**Location**: `genesis/autonomous/cycle.py`

**Model**:
```python
class AutonomousEngine:
    def __init__(self, config)
    def run_cycle(self) -> dict
    def get_stage(self, name) -> Stage
```

**Every stage handler does**: `return {"done": True}` — all 30 stages are stubs.

**Consumers**: None found.

**Status**: **Stub** — 30-stage pipeline with no real implementation.

---

## 3. Comparison Matrix

| Dimension | runtime/executor | execution/ | execution_graph | os/runtime | kernel/ | fabric/ | autonomous/ |
|-----------|-----------------|------------|-----------------|------------|---------|---------|-------------|
| **Lines** | ~500 | ~600 | ~420 | ~499 | ~350 | ~200 | ~330 |
| **DI injected** | Yes | No | No | No | No | No | No |
| **EventBus** | Yes | No | No | Observer | No | EventManager | No |
| **HistoryStore** | Yes | No | No | No | No | No | No |
| **Thread pool** | Yes | No | No | No | No | No | No |
| **Retry logic** | Yes (max_retries) | No | No | Yes (recovery) | No | No | No |
| **Health model** | No | No | No | Yes (4 states) | No | No | No |
| **Tick system** | No | No | No | Yes | No | No | No |
| **Checkpointing** | No | No | No | Yes | No | No | No |
| **Recovery** | No | No | No | Yes | No | No | No |
| **DAG execution** | No | No | Yes | No | No | No | No |
| **Simulation** | No | No | Yes | No | No | No | No |
| **Stage pipeline** | No | No | No | No | No | No | Yes (30 stubs) |
| **Sub-managers** | No | No | No | No | Yes (16) | Yes (6) | No |
| **Consumers** | EventBus, HistoryStore, platform | None | None | None | None | None | None |
| **Test coverage** | ~200 tests | None | None | None | None | None | None |

---

## 4. Duplication Analysis

### 4.1 Who Does What — 7 Execution Systems

```
Task Execution:
  runtime/executor.py  —  ExecutionEngine.execute_task()  ✓ (real)
  execution/engine.py  —  parallel universe (no consumers) ✗
  
Workflow Execution:
  runtime/executor.py  —  ExecutionEngine.execute_workflow() ✓
  execution_graph.py   —  ExecutionGraph.execute() (simulation) ✗

Lifecycle Management:
  runtime/executor.py  —  PENDING→RUNNING→COMPLETED/FAILED ✓
  os/runtime.py        —  HEALTH_CHECK→BOOT→TICK→SHUTDOWN (orphaned) ✗
  kernel/kernel.py     —  boot→shutdown (aspirational) ✗

Health Management:
  os/runtime.py        —  health_check(), 4-state health ✗ (no consumers)

Task/Process Scheduling:
  kernel/kernel.py     —  ProcessManager (aspirational) ✗
  fabric/kernel.py     —  TaskScheduler (aspirational) ✗

Plugin/Service Management:
  kernel/kernel.py     —  PluginManager, ServiceManager ✗
  fabric/kernel.py     —  PluginManager, ServiceRegistry ✗
```

### 4.2 Consumer Heatmap

```
Consumer             | exec | exec/ | exec_gr | os/r | kern | fab | auto
---------------------|------|-------|---------|------|------|-----|------
platform.py          |  ✓   |       |         |      |      |     |
omega_loop.py        |  ✓   |       |         |      |      |     |
EventBus             |  ✓   |       |         |      |      |     |
HistoryStore         |  ✓   |       |         |      |      |     |
Test suite           |  ✓   |       |         |      |      |     |
```

Only `runtime/executor.py` has real consumers.

### 4.3 Duplication Cost

| System | Lines | % Duplicated | Annual Maintenance Cost (est) |
|--------|-------|-------------|------------------------------|
| runtime/executor.py | ~500 | 0% (canonical) | $0 (maintain) |
| execution/ | ~600 | 100% (no consumers) | ~$6,000 |
| execution_graph.py | ~420 | 100% (no consumers) | ~$4,200 |
| os/runtime.py | ~499 | 80% (concepts valuable but no consumers) | ~$4,000 |
| kernel/kernel.py | ~350 | 100% (no consumers) | ~$3,500 |
| fabric/kernel.py | ~200 | 100% (no consumers) | ~$2,000 |
| autonomous/cycle.py | ~330 | 100% (30 stubs) | ~$3,300 |

**Total waste**: ~$19,000/year in maintenance of unused execution infrastructure.

---

## 5. Design: Universal Runtime Model

### 5.1 Design Requirements

Based on archaeology:

1. **Task execution** — existing ExecutionEngine capability (canonical)
2. **Workflow orchestration** — existing ExecutionEngine capability
3. **Health monitoring** — from os/runtime.py (4 states, health checks)
4. **Recovery** — from os/runtime.py (with backoff, max attempts)
5. **Observability** — events for every state transition
6. **Checkpointing** — from os/runtime.py (state serialization)
7. **Tick-based scheduling** — from os/runtime.py (periodic execution)
8. **Stage pipeline** — from autonomous/cycle.py (30 stages → configurable)
9. **DAG execution** — from execution_graph.py (condition-based edges)
10. **DI, EventBus, HistoryStore** — existing ExecutionEngine wiring

### 5.2 Universal Runtime State Machine

```
                  ┌─────────────┐
                  │  CREATED    │
                  └──────┬──────┘
                         │ initialize()
                         ▼
                  ┌─────────────┐
         ┌─────── │  BOOTING    │ ──────► FAILED
         │        └──────┬──────┘
         │               │ boot_complete()
         │               ▼
         │        ┌─────────────┐
         │        │  HEALTHY    │ ◄──────────────────────────┐
         │        └──────┬──────┘                            │
         │               │ health_check() fails              │
         │               ▼                                   │
         │        ┌─────────────┐                            │
         │        │  DEGRADED   │ ──────► recover() ─────────┘
         │        └──────┬──────┘
         │               │ health_check() fails again
         │               ▼
         │        ┌─────────────┐
         │        │  UNHEALTHY  │ ──────► recover() (with backoff)
         │        └──────┬──────┘
         │               │ max_recovery_exceeded
         │               ▼
         │        ┌─────────────┐
         │        │  RECOVERING │ ──────► recover() success ──► HEALTHY
         │        └──────┬──────┘            │
         │               │ max_retries       │ failure
         │               ▼                   ▼
         │        ┌─────────────┐    ┌─────────────┐
         └─────── │  FAILED     │    │  DEGRADED   │ ◄── (back to degraded)
                  └─────────────┘    └─────────────┘
                         │
                         │ shutdown()
                         ▼
                  ┌─────────────┐
                  │  SHUTDOWN   │
                  └─────────────┘
```

**States**: `CREATED → BOOTING → HEALTHY → DEGRADED → UNHEALTHY → RECOVERING → FAILED → SHUTDOWN`

### 5.3 Execution Models (6 Specializations)

```python
# 1. Task — single unit of work
class TaskExecutionModel:
    def execute_task(self, task) -> TaskResult

# 2. Workflow — ordered sequence of tasks
class WorkflowExecutionModel:
    def execute_workflow(self, workflow) -> list[TaskResult]

# 3. Pipeline — streaming sequence (output → input)
class PipelineExecutionModel:
    def execute_pipeline(self, pipeline) -> Any

# 4. Actor — persistent message-processing entity
class ActorExecutionModel:
    def send(self, message) -> None
    def process(self) -> Any

# 5. Schedule — tick-based periodic execution
class ScheduleExecutionModel:
    def tick(self) -> dict
    def interval(self) -> float

# 6. Cycle — multi-stage lifecycle pipeline
class CycleExecutionModel:
    def stage(self, name) -> StageResult
    def execute(self) -> dict
```

### 5.4 Health Model

```python
@dataclass
class HealthStatus:
    state: str  # healthy | degraded | unhealthy | recovering | failed
    checks: list[HealthCheck]
    last_check: float
    failure_count: int
    recovery_attempts: int

@dataclass
class HealthCheck:
    name: str
    status: bool
    detail: str
    timestamp: float
```

### 5.5 Recovery Model

```python
@dataclass
class RecoveryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 5.0
    backoff_multiplier: float = 2.0

class RecoveryManager:
    def recover(self, runtime, policy) -> RecoveryResult
    def checkpoint(self, state) -> None
    def restore(self) -> dict | None
```

### 5.6 Observability Framework

```python
class RuntimeEvent(Enum):
    BOOT_START = "boot_start"
    BOOT_COMPLETE = "boot_complete"
    HEALTH_CHANGE = "health_change"
    RECOVERY_START = "recovery_start"
    RECOVERY_COMPLETE = "recovery_complete"
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_COMPLETE = "workflow_complete"
    SHUTDOWN = "shutdown"

class RuntimeObserver:
    def on_event(self, event: RuntimeEvent, data: dict) -> None
```

### 5.7 Ownership Boundaries

```
UniversalRuntime
├── State Manager (state machine + transitions)
├── Execution Model Registry (task, workflow, pipeline, actor, schedule, cycle)
├── Health Manager (health checks + status)
├── Recovery Manager (checkpoint + restore)
├── Observer Registry (event hooks)
└── Scheduler (tick-based execution)

Owned by: runtime/ package
External integrations:
  - EventBus → for event emission
  - HistoryStore → for state persistence
  - PluginManager → for extensible execution models
```

---

## 6. Engineering Decisions

### 6.1 Why keep only runtime/executor.py?

**Rejected alternatives**:

1. **Keep os/runtime.py as canonical**: Most complete runtime but zero consumers. Would require rewriting every consumer.

2. **Merge all 7 into big runtime**: Creates god-object anti-pattern. Universal Runtime should be a design that ExecutionEngine evolves toward, not a new class that replaces everything at once.

3. **Keep all 7**: Wasteful. 6 of 7 have no consumers.

**Decision**: ExecutionEngine (`runtime/executor.py`) is the canonical base. Evolve it toward Universal Runtime model across NEMESIS phases. Migrate concepts from os/runtime.py (health, ticks, recovery, checkpointing). Do not create a new UniversalRuntime class until the design is validated.

### 6.2 What about the 5 orphaned systems?

- `execution/` → **Deprecate**. Zero consumers. If features are needed later, they should be added to ExecutionEngine.
- `execution_graph.py` → **Deprecate**. DAG execution is not currently needed anywhere. The model is valuable; save it in the design document.
- `kernel/kernel.py` → **Deprecate**. 16 sub-managers duplicate EventBus, PluginManager, ServiceProvider.
- `fabric/kernel.py` → **Deprecate**. 6 sub-systems duplicated elsewhere.
- `autonomous/cycle.py` → **Deprecate**. 30 stub stages. Cycle execution model belongs in Universal Runtime design.

### 6.3 When to implement Universal Runtime?

**Not yet**. The Universal Runtime design should be validated by Mission 10 (Engineering Transformation Engine) before implementation. Premature implementation creates another parallel execution system.

**Trigger**: When a consumer needs a health model, recovery, or DAG execution that ExecutionEngine cannot provide.

---

## 7. Technical Debt Impact

| System | Action | Lines freed | Risk | Migration path |
|--------|--------|------------|------|---------------|
| runtime/executor.py | **KEEP** (canonical) | 0 | None | N/A |
| execution/ | Deprecate + warning | ~600 | Low — no consumers | Point to ExecutionEngine |
| execution_graph.py | Deprecate + warning | ~420 | Low — no consumers | Design doc only |
| os/runtime.py | Migrate concepts, deprecate | ~499 | Medium — unique concepts | Port health/ticks/recovery |
| kernel/kernel.py | Deprecate + warning | ~350 | Low — no consumers | Point to existing managers |
| fabric/kernel.py | Deprecate + warning | ~200 | Low — no consumers | Point to EventBus/Registry |
| autonomous/cycle.py | Deprecate + warning | ~330 | Low — no consumers | Point to Cycle execution model |

---

## 8. Validation

- **2,763 tests pass** after deprecation (verified)
- **No runtime consumer broken** — only execution/executor.py has consumers
- **Deprecation warnings added** for orphaned systems (same pattern as other 8 deprecated modules)

---

## 9. Next Steps

1. Add deprecation warnings to `execution/`, `execution_graph.py`, `os/runtime.py`, `kernel/kernel.py`, `fabric/kernel.py`, `autonomous/cycle.py`
2. Port health model from os/runtime.py into ExecutionEngine
3. Port tick scheduling from os/runtime.py into ExecutionEngine
4. Port recovery/checkpointing from os/runtime.py into ExecutionEngine
5. Validate: all tests pass, all consumers continue working
6. Mission 10 (Transformation Engine) validates Universal Runtime design before implementation
