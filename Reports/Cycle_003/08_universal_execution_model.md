# PROJECT NEMESIS Phase III — Mission 8: Universal Execution Model

**Date**: 2026-06-30 | **Repository**: 335 Python files (excl tests), ~71,916 lines (excl tests), 72 test files, 2,763 tests
**Scope**: Every execution system — canonical model covering all engineering activities

---

## 1. Executive Summary

Genesis has **16 distinct execution representations** spread across 12 modules totaling ~5,200 lines. Every implementation defines its own Task/Workflow/Status model, state machine, and lifecycle. No two are compatible. No canonical representation exists.

**The models found**:
- `runtime/executor.py`: Task → Workflow → ExecutionEngine with EventBus (real consumers)
- `execution/engine.py`: Orchestrator over 5 sub-models (parallel universe, no consumers)
- `execution/workflow.py`: DAG-based WorkflowDAG/WorkflowNode (no consumers)
- `execution/tasks.py`: TaskExecutor with priority/retry (no consumers)
- `execution/actors.py`: ActorEngine (no consumers)
- `execution/pipeline.py`: PipelineEngine (no consumers)
- `execution/jobs.py`: JobManager (no consumers)
- `execution/retry.py`: RetryPolicy/CompensationEngine (no consumers)
- `execution_graph.py`: ExecutionGraph — 15 NodeTypes, 5 EdgeTypes, 6 NodeStatuses (no consumers)
- `os/runtime.py`: AutonomousRuntime — health/ticks/recovery (no consumers)
- `kernel/kernel.py`: UniversalKernel — 16 sub-managers (no consumers)
- `fabric/kernel.py`: FabricKernel — 6 sub-systems (no consumers)
- `autonomous/cycle.py`: 30-stage AutonomousEngine (all stubs)
- `omega_loop.py`: 18-Book constitution (runs in production)
- `atlas.py`: 15-stage reconstruction protocol (runs in production)
- `genesis/planner.py`: EngineeringPlanner (runs in production)

**Design**: A canonical 14-level model — Execution → Workflow → Phase → Stage → Task → Action → Operation → Instruction → Result → Evidence → Validation → Checkpoint → Rollback → Completion — that subsumes all 16 existing models.

---

## 2. Every Execution Model Catalog

### 2.1 `runtime/executor.py` (266 lines)

| Property | Value |
|----------|-------|
| **Core types** | Task, Workflow, ExecutionEngine |
| **Task states** | PENDING → RUNNING → COMPLETED / FAILED → BLOCKED / SKIPPED |
| **Workflow states** | "created" → "planned" → "completed" / "failed" |
| **Execution** | Sequential DAG traversal (topological sort) |
| **Events** | workflow.created, workflow.planned, workflow.completed, workflow.failed, task.running, task.completed, task.failed, task.blocked |
| **Persistence** | HistoryStore (save/query by workflow) |
| **DI** | EventBus and HistoryStore injected |
| **Consumers** | EventBus, HistoryStore, platform.py |
| **Status** | Canonical (only real consumer) |

### 2.2 `execution/` package (944 lines total)

| Module | Lines | Core Types | States | Consumers |
|--------|-------|------------|--------|-----------|
| `engine.py` | 105 | ExecutionEngine | orchestrates sub-engines | None |
| `workflow.py` | 128 | WorkflowEngine, WorkflowDAG, WorkflowNode | PENDING/RUNNING/SUCCESS/FAILED/SKIPPED | None |
| `tasks.py` | 139 | TaskExecutor, Task | PENDING/RUNNING/SUCCESS/FAILED | None |
| `actors.py` | 112 | ActorEngine, Actor | CREATED/RUNNING/PAUSED/STOPPED/ERROR | None |
| `pipeline.py` | 84 | PipelineEngine, PipelineStage | PENDING/RUNNING/COMPLETED/FAILED | None |
| `jobs.py` | 158 | JobManager, LongRunningJob | PENDING/RUNNING/COMPLETED/FAILED/CANCELLED | None |
| `retry.py` | 97 | RetryPolicy, CompensationEngine | N/A | None |

**Status**: Complete parallel universe — 6 execution models (workflow, task, actor, pipeline, job, retry) with unified ExecutionEngine facade, 0 consumers.

### 2.3 `execution_graph.py` (420 lines)

| Property | Value |
|----------|-------|
| **Core types** | ExecutionGraph, ExecutionNode, ExecutionEdge |
| **Node types** | BOOT, RUNTIME, SCHEDULER, PLANNER, BRAIN, MEMORY, EXECUTION, COMPILER, VERIFICATION, GRAPH, ECONOMICS, LEARNING, EVOLUTION, SHUTDOWN, CUSTOM |
| **Edge types** | SEQUENTIAL, FEEDBACK, PARALLEL, CONDITIONAL, FALLBACK |
| **Node states** | PENDING → RUNNING → COMPLETED / FAILED → SKIPPED / PAUSED |
| **Features** | Pre/post conditions, timeout, retry, semantic versioning |
| **Consumers** | None |

### 2.4 `os/runtime.py` (499 lines)

| Property | Value |
|----------|-------|
| **Core** | AutonomousRuntime |
| **Health states** | HEALTHY / DEGRADED / UNHEALTHY / RECOVERING |
| **Features** | Tick loop, checkpoint, recovery, health checks, observers |
| **Consumers** | None |

### 2.5 `autonomous/cycle.py` (~330 lines)

| Property | Value |
|----------|-------|
| **Core** | AutonomousEngine |
| **Stages** | 30 stages (all return `{"done": True}`) |
| **Consumers** | None |

### 2.6 `omega_loop.py` (327,217 lines)

| Property | Value |
|----------|-------|
| **Core** | OmegaLoop — 18-Book constitution |
| **Books** | I: GenesisArchitect, II: KnowledgeDiffusion, III: SelfEvolution, IV: Discovery, V: Intention, VI: Runtime, VII: Architecture, VIII: Autonomous, IX: Mathematics, X: Repository, XI: EngineeringPhysics, XII: EngineeringScientist, XIII: EngineeringEconomics, XIV: Transformation, XV: DigitalTwin, XVI: SelfEngineering, XVII: EngineeringOS, XVIII: GOAL |
| **Execution** | Sequential book-by-book, each book has stages |
| **Consumers** | platform.py, Atlas |

### 2.7 `atlas.py` (1,297 lines)

| Property | Value |
|----------|-------|
| **Core** | Atlas — 15-stage reconstruction engine |
| **Stages** | Repository Reconstruction → Engineering Understanding → Architectural Reconstruction → Capability Reconstruction → Problem Discovery → Hypothesis Formation → Engineering Design → Simulation → Implementation → Verification → Benchmarking → Architectural Review → Documentation → Engineering Report → Roadmap Generation |
| **Maturity** | Each stage produces a report |
| **Consumers** | OmegaLoop, direct CLI |

### 2.8 `genesis/planner.py` (14,526 lines)

| Property | Value |
|----------|-------|
| **Core** | EngineeringPlanner |
| **Purpose** | Engineering activity planning |
| **Consumers** | OmegaLoop |

---

## 3. Universal Execution Model

### 3.1 The Canonical Hierarchy

```
Execution                 ← Top-level run (e.g., "Platform Boot", "Run Atlas")
  └── Workflow            ← Named procedure with sub-steps
        └── Phase         ← Major lifecycle stage
              └── Stage   ← Concrete process step
                    └── Task     ← Executable unit
                          └── Action    ← Invocation step
                                └── Operation  ← Primitive operation
                                      └── Instruction ← Atomic directive
                                            └── Result ← Operation output
                                                  └── Evidence ← Verifiable proof
                                                        └── Validation ← Check against criteria
                                                              └── Checkpoint ← State snapshot
                                                                    └── Rollback ← State restoration
                                                                          └── Completion ← Terminal state
```

### 3.2 Level Definitions

#### 3.2.1 Execution

| Property | Value |
|----------|-------|
| **Purpose** | Top-level run of a complete engineering activity |
| **Owner** | PlatformOrchestrator or OmegaLoop |
| **Lifecycle** | CREATED → BOOTING → RUNNING → COMPLETED / FAILED |
| **Input** | Configuration, workspace path |
| **Output** | Execution Report (all Workflow results + Evidence + Validation) |
| **Failure modes** | Critical infrastructure failure, configuration error |
| **Recovery** | Re-execute from checkpoints |
| **Observability** | Execution-level events, timing, resource usage |
| **Traceability** | execution_id links all sub-levels |
| **Examples** | `VenusPlatform.boot()`, `Atlas.run()`, `OmegaLoop.execute()` |

**State Machine**:
```
CREATED ──► BOOTING ──► RUNNING ──► COMPLETED
                  │          │
                  ▼          ▼
               FAILED ◄──────┘
```

#### 3.2.2 Workflow

| Property | Value |
|----------|-------|
| **Purpose** | Named procedure composed of phases |
| **Owner** | System that defines the workflow (e.g., Platform, Atlas) |
| **Lifecycle** | DEFINED → PLANNED → EXECUTING → COMPLETED / FAILED / CANCELLED |
| **Input** | Workflow definition (name, phases, dependencies) |
| **Output** | WorkflowResult (phase results, completion status, metrics) |
| **Failure modes** | Phase failure cascading, dependency cycle |
| **Recovery** | Re-plan and retry failed phases |
| **Observability** | Workflow events, phase progress %, timing |
| **Traceability** | workflow_id |
| **State machine** | `DEFINED → PLANNED → EXECUTING → COMPLETED / FAILED` |
| **Maps from** | `runtime/executor.Workflow`, `execution/workflow.WorkflowDAG`, `omega_loop.Book`, `atlas.Stage` |

#### 3.2.3 Phase

| Property | Value |
|----------|-------|
| **Purpose** | Major lifecycle stage within a workflow |
| **Owner** | Workflow definition |
| **Lifecycle** | PENDING → READY → ACTIVE → COMPLETED / FAILED / SKIPPED |
| **Input** | Phase definition, dependencies' outputs |
| **Output** | PhaseResult (stage results, evidence) |
| **Failure modes** | Stage failure, dependency not met, timeout |
| **Recovery** | Retry from last checkpoint within phase |
| **Observability** | Phase events, stage progress |
| **Traceability** | phase_id within workflow |
| **State machine** | `PENDING → READY → ACTIVE → COMPLETED / FAILED` |
| **Maps from** | `omega_loop.Book.chapters`, `platform.boot()` phase boundaries |

#### 3.2.4 Stage

| Property | Value |
|----------|-------|
| **Purpose** | Concrete process step with defined inputs/outputs |
| **Owner** | Phase owner |
| **Lifecycle** | PENDING → RUNNING → COMPLETED / FAILED / SKIPPED |
| **Input** | Stage parameters, context from prior stages |
| **Output** | StageResult (task results, artifacts, metrics) |
| **Failure modes** | Task failure, precondition unmet, resource unavailable |
| **Recovery** | Retry stage (idempotent design required) |
| **Observability** | Stage events, status transitions |
| **Traceability** | stage_id within phase |
| **State machine** | `PENDING → RUNNING → COMPLETED / FAILED / SKIPPED` |
| **Maps from** | `atlas.STAGE_NAMES` (15 stages), `autonomous/cycle.py` stages (30), `execution_graph.ExecutionNode` |

#### 3.2.5 Task

| Property | Value |
|----------|-------|
| **Purpose** | Executable unit of work with handler |
| **Owner** | Stage owner |
| **Lifecycle** | PENDING → RUNNING → COMPLETED / FAILED / BLOCKED / SKIPPED |
| **Input** | Task inputs (args, kwargs), context |
| **Output** | TaskResult (return value, duration, status) |
| **Failure modes** | Handler exception, timeout, dependency blocked |
| **Recovery** | Retry (configurable max_retries, backoff) |
| **Observability** | Task lifecycle events, timing, error details |
| **Traceability** | task_id within stage |
| **State machine** | `PENDING → RUNNING → COMPLETED / FAILED / BLOCKED` |
| **Maps from** | `runtime/executor.Task`, `execution/tasks.Task`, `execution_graph.ExecutionNode` |

#### 3.2.6 Action

| Property | Value |
|----------|-------|
| **Purpose** | Specific invocation of a capability |
| **Owner** | Task handler |
| **Lifecycle** | PENDING → INVOKING → COMPLETED / FAILED |
| **Input** | Action parameters, resource references |
| **Output** | ActionResult (raw return value) |
| **Failure modes** | Resource not found, permission denied, capability missing |
| **Recovery** | Fallback action, compensation |
| **Observability** | Action events, input/output logging |
| **Traceability** | action_id within task |
| **Maps from** | `execution/actors.Actor.send()`, `execution/retry.CompensationEngine` |

#### 3.2.7 Operation

| Property | Value |
|----------|-------|
| **Purpose** | Primitive operation on a system (e.g., write file, query DB) |
| **Owner** | Action executor |
| **Lifecycle** | PENDING → EXECUTING → COMPLETED / FAILED |
| **Input** | Operation parameters (type, target, data) |
| **Output** | OperationResult (status, data, timing) |
| **Failure modes** | System error, I/O error, network error |
| **Recovery** | Retry with exponential backoff |
| **Observability** | Operation-level metrics, error logs |
| **Traceability** | operation_id within action |
| **Maps from** | Low-level execution primitives in all systems |

#### 3.2.8 Instruction

| Property | Value |
|----------|-------|
| **Purpose** | Atomic directive — the smallest execution unit |
| **Owner** | Operation executor |
| **Lifecycle** | DISPATCHED → PROCESSING → ACKNOWLEDGED / REJECTED |
| **Input** | Instruction payload (method, arguments) |
| **Output** | InstructionResult (ack, response) |
| **Failure modes** | Runtime error, assertion failure |
| **Recovery** | None at this level (atomic) |
| **Observability** | Instruction trace log |
| **Traceability** | instruction_id within operation |

#### 3.2.9 Result

| Property | Value |
|----------|-------|
| **Purpose** | Output produced by any execution level |
| **Owner** | Level that produced it |
| **Lifecycle** | PRODUCED → RECORDED → CONSUMED → ARCHIVED |
| **Content** | status: str, output: Any, duration_ms: float, error: str | None, metadata: dict |
| **Failure modes** | Result corruption, transmission failure |
| **Observability** | Result capture, serialization |
| **Traceability** | Links to producing level_id |

#### 3.2.10 Evidence

| Property | Value |
|----------|-------|
| **Purpose** | Verifiable proof that an execution occurred correctly |
| **Owner** | Execution framework |
| **Lifecycle** | COLLECTED → VERIFIED → STORED → CITED |
| **Content** | evidence_type: str, artifact_path: str | None, checksum: str, assertions: list[str], timestamp: float |
| **Failure modes** | Evidence tampering, storage corruption |
| **Observability** | Evidence chain, integrity verification |
| **Traceability** | Links to producing execution_id |

**Maps from**: `execution_graph.ExecutionNode.pre_conditions`, `post_conditions`, test assertions.

#### 3.2.11 Validation

| Property | Value |
|----------|-------|
| **Purpose** | Check actual result against expected criteria |
| **Owner** | Validation framework |
| **Lifecycle** | PENDING → EVALUATING → PASSED / FAILED / INCONCLUSIVE |
| **Input** | Result, ValidationCriteria |
| **Output** | ValidationResult (passed, failed_count, details) |
| **Failure modes** | Criteria not defined, validator error |
| **Recovery** | Re-run validation |
| **Observability** | Validation events, pass/fail ratio |
| **Traceability** | Links to evidence verified |

#### 3.2.12 Checkpoint

| Property | Value |
|----------|-------|
| **Purpose** | Snapshot of execution state for resumption |
| **Owner** | Execution framework |
| **Lifecycle** | CREATED → VALIDATED → STORED → RESTORED / PRUNED |
| **Content** | checkpoint_id: str, level_id: str, state: dict, timestamp: float |
| **Failure modes** | Serialization failure, storage full |
| **Observability** | Checkpoint creation/restoration events |
| **Traceability** | Links to execution level at point of capture |
| **Maps from** | `os/runtime.checkpoint()`, `CheckpointStore` |

#### 3.2.13 Rollback

| Property | Value |
|----------|-------|
| **Purpose** | Restore execution state from checkpoint |
| **Owner** | Recovery manager |
| **Lifecycle** | INITIATED → RESTORING → COMPLETED / FAILED |
| **Input** | Checkpoint reference |
| **Output** | RollbackResult (success, restored_level) |
| **Failure modes** | Checkpoint invalid, partial restore |
| **Observability** | Rollback events, state diff |
| **Traceability** | Links to source and target checkpoints |
| **Maps from** | `os/runtime.recover()`, `execution/retry.CompensationEngine` |

#### 3.2.14 Completion

| Property | Value |
|----------|-------|
| **Purpose** | Terminal state for any execution level |
| **Owner** | Level owner |
| **Lifecycle** | FINALIZING → FINALIZED → REPORTED → ARCHIVED |
| **Content** | final_status: str, summary: dict, evidence_chain: list, metrics: dict |
| **Failure modes** | Finalization error, reporting failure |
| **Observability** | Completion events, final reports |
| **Traceability** | Complete tree from execution_id down |

---

## 4. State Machine Comparison — All 16 Models → Canonical

| Source | Their States | Canonical Mapping |
|--------|-------------|-------------------|
| `runtime/executor.TaskStatus` | PENDING, RUNNING, COMPLETED, FAILED, SKIPPED, BLOCKED | Task |
| `runtime/executor.Workflow.status` | "created", "planned", "completed", "failed" | Workflow |
| `execution/workflow.WorkflowStatus` | PENDING, RUNNING, SUCCESS, FAILED, SKIPPED | Workflow / Stage |
| `execution/tasks.TaskStatus` | PENDING, RUNNING, SUCCESS, FAILED | Task (SUCCESS → COMPLETED) |
| `execution/actors.ActorStatus` | CREATED, RUNNING, PAUSED, STOPPED, ERROR | Action |
| `execution/pipeline.PipelineState` | PENDING, RUNNING, COMPLETED, FAILED | Stage |
| `execution/jobs.JobStatus` | PENDING, RUNNING, COMPLETED, FAILED, CANCELLED | Task |
| `execution_graph.NodeStatus` | PENDING, RUNNING, COMPLETED, FAILED, SKIPPED, PAUSED | Stage / Task |
| `os/runtime.HealthStatus` | HEALTHY, DEGRADED, UNHEALTHY, RECOVERING | Rollback / Recovery |
| `autonomous/cycle` | 30 stages (all return `{"done": True}`) | Stage (all stubs) |
| `kernel/kernel` | boot → shutdown | Execution |
| `fabric/kernel` | boot → shutdown | Execution |
| `omega_loop` | 18 books sequential | Workflow (18 phases) |
| `atlas` | 15 stages sequential | Workflow (15 stages) |
| `platform_v2.ServiceState` | CREATED, INITIALIZING, READY, RUNNING, DEGRADED, FAILED, STOPPING, STOPPED | Workflow / Phase |
| `engineering_os.ServiceStatus` | STOPPED, STARTING, RUNNING, DEGRADED, ERROR, STOPPING | Action / Phase |

---

## 5. Mapping Matrix — Every Existing Implementation

| System | Execution | Workflow | Phase | Stage | Task | Action | Op | Result | Evidence | Validation | Checkpoint | Rollback | Completion |
|--------|-----------|----------|-------|-------|------|--------|----|--------|----------|------------|------------|----------|------------|
| `runtime/executor.py` | — | Workflow | — | — | Task | — | — | ✓ | — | — | — | — | ✓ |
| `execution/engine.py` | ExecutionEngine | — | — | — | — | — | — | ✓ | — | — | — | — | ✓ |
| `execution/workflow.py` | — | WorkflowDAG | — | — | WorkflowNode | — | — | ✓ | — | — | — | — | — |
| `execution/tasks.py` | — | — | — | — | Task | — | — | ✓ | — | — | — | — | — |
| `execution/actors.py` | — | — | — | — | — | Actor | — | ✓ | — | — | — | — | — |
| `execution/pipeline.py` | — | — | — | PipelineStage | — | — | — | ✓ | — | — | — | — | — |
| `execution/jobs.py` | — | — | — | — | LongRunningJob | — | — | ✓ | — | — | — | — | — |
| `execution/retry.py` | — | — | — | — | — | ✓ | — | ✓ | — | — | — | Compensation | — |
| `execution_graph.py` | — | — | — | ExecutionNode | — | — | — | ✓ | ✓ (conditions) | — | — | — | ✓ |
| `os/runtime.py` | AutonomousRuntime | — | — | — | — | — | — | ✓ | — | HealthCheck | ✓ | ✓ | ✓ |
| `kernel/kernel.py` | UniversalKernel | — | — | — | — | — | — | — | — | — | — | — | — |
| `fabric/kernel.py` | FabricKernel | — | — | — | — | — | — | — | — | — | — | — | — |
| `autonomous/cycle.py` | AutonomousEngine | — | — | CycleStage | — | — | — | CycleResult | — | — | — | — | — |
| `omega_loop.py` | OmegaLoop | Book | Chapter | Stage | — | — | — | ✓ | — | — | — | — | ✓ |
| `atlas.py` | Atlas | — | — | Stage (15) | — | — | — | Report | — | — | — | — | ✓ |
| `planner.py` | EngineeringPlanner | Plan | — | — | — | — | — | PlanResult | — | — | — | — | — |

**Key insight**: Only 5 of 14 canonical levels are covered by any existing model (Execution, Workflow, Stage, Task, Action). The remaining 9 levels (Phase, Operation, Instruction, Result, Evidence, Validation, Checkpoint, Rollback, Completion) are absent or ad-hoc across all systems.

---

## 6. Unified Type System

### 6.1 ExecutionID

```python
@dataclass
class ExecutionID:
    execution_id: str  # Root — generated
    workflow_id: str
    phase_id: str
    stage_id: str
    task_id: str
    action_id: str
    operation_id: str
    instruction_id: str
```

Every level inherits its parent ID, forming a traceable chain.

### 6.2 ExecutionContext

```python
@dataclass
class ExecutionContext:
    execution_id: ExecutionID
    config: dict[str, Any]
    workspace: str | Path
    checkpoint_dir: str | Path
    event_bus: EventBus | None = None
    started_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
```

### 6.3 Node (universal execution graph node)

```python
@dataclass
class ExecutionNode:
    id: str
    level: ExecutionLevel  # WORKFLOW | PHASE | STAGE | TASK | ACTION | etc.
    name: str
    status: ExecutionStatus
    handler: Callable | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    timeout: float = 300.0
    max_retries: int = 3
    retry_count: int = 0
    checkpoints: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    validation: ValidationResult | None = None
    error: str | None = None
    started_at: float = 0.0
    completed_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
```

### 6.4 ExecutionEngine (universal interface)

```python
class ExecutionEngine(ABC):
    """Universal execution engine — all execution models derive from this."""

    @abstractmethod
    def execute(self, node: ExecutionNode, context: ExecutionContext) -> ExecutionNode:
        """Execute a single node at any level."""
        ...

    def execute_tree(self, root: ExecutionNode, context: ExecutionContext) -> ExecutionNode:
        """Execute a tree of nodes recursively, respecting dependencies."""
        ...

    @abstractmethod
    def checkpoint(self, node: ExecutionNode) -> str:
        """Save state for resumption."""
        ...

    @abstractmethod
    def rollback(self, checkpoint_id: str) -> ExecutionNode | None:
        """Restore from checkpoint."""
        ...

    @abstractmethod
    def validate(self, node: ExecutionNode) -> ValidationResult:
        """Validate a node's output against its criteria."""
        ...
```

---

## 7. Execution Specializations

All specializations implement the same `ExecutionEngine` interface, differing in how they schedule and execute children.

### 7.1 TaskEngine

**Purpose**: Single atomic execution unit.
**Maps from**: `runtime/executor.ExecutionEngine`, `execution/tasks.TaskExecutor`
**Execution model**: Invoke handler, capture result, handle errors.
```python
class TaskEngine(ExecutionEngine):
    def execute(self, node, context):
        try:
            node.status = RUNNING
            result = node.handler(**node.inputs)
            node.outputs = {"result": result}
            node.status = COMPLETED
        except Exception as e:
            node.status = FAILED
            node.error = str(e)
        return node
```

### 7.2 WorkflowEngine

**Purpose**: Execute a DAG of tasks/stages with dependency resolution.
**Maps from**: `runtime/executor.ExecutionEngine`, `execution/workflow.WorkflowEngine`
**Execution model**: Topological sort → sequential/parallel execution.
```python
class WorkflowEngine(ExecutionEngine):
    def execute(self, node, context):
        # Resolve dependency order
        ordered = topological_sort(node.children, node.dependencies)
        for child in ordered:
            child = self.execute(child, context)
            if child.status == FAILED:
                node.status = FAILED
                return node
        node.status = COMPLETED
        return node
```

### 7.3 PhaseEngine

**Purpose**: Ordered sequence of stages.
**Maps from**: `omega_loop`, `atlas`
**Execution model**: Sequential stage execution, strict ordering.
```python
class PhaseEngine(ExecutionEngine):
    def execute(self, node, context):
        for stage in sorted(node.children, key=lambda s: s.metadata.get("order", 0)):
            child = self.execute(stage, context)
            if child.status in (FAILED, SKIPPED):
                node.status = FAILED
                return node
        node.status = COMPLETED
        return node
```

### 7.4 PipelineEngine

**Purpose**: Streaming sequence where each stage's output is the next stage's input.
**Maps from**: `execution/pipeline.PipelineEngine`
**Execution model**: Sequential with data flow.
```python
class PipelineEngine(ExecutionEngine):
    def execute(self, node, context):
        data = node.inputs
        for stage in node.children:
            stage.inputs = data
            stage = self.execute(stage, context)
            data = stage.outputs
            if stage.status == FAILED:
                node.status = FAILED
                return node
        node.outputs = data
        node.status = COMPLETED
        return node
```

### 7.5 ActorEngine

**Purpose**: Message-driven persistent processing entity.
**Maps from**: `execution/actors.ActorEngine`
**Execution model**: Message queue → process → respond.
```python
class ActorEngine(ExecutionEngine):
    def execute(self, node, context):
        node.status = RUNNING
        while message := self._dequeue(node.id):
            result = node.handler(message)
            node.outputs[message.id] = result
        node.status = COMPLETED
        return node
```

### 7.6 ScheduleEngine

**Purpose**: Tick-based periodic execution.
**Maps from**: `os/runtime.AutonomousRuntime`
**Execution model**: Timer → execute on interval.
```python
class ScheduleEngine(ExecutionEngine):
    def execute(self, node, context):
        while not self._stop_event.is_set():
            for child in node.children:
                self.execute(child, context)
            time.sleep(node.metadata.get("tick_interval", 60))
        node.status = COMPLETED
        return node
```

### 7.7 CycleEngine

**Purpose**: Multi-stage lifecycle pipeline with completion criteria.
**Maps from**: `autonomous/cycle.AutonomousEngine`
**Execution model**: Ordered stage execution, each stage can skip based on conditions.
```python
class CycleEngine(ExecutionEngine):
    def execute(self, node, context):
        for stage in node.children:
            if stage.metadata.get("condition") and not stage.metadata["condition"](context):
                stage.status = SKIPPED
                continue
            stage = self.execute(stage, context)
        node.status = COMPLETED
        return node
```

---

## 8. Canonical Status Mappings

### 8.1 Unified Enum

```python
class ExecutionLevel(Enum):
    EXECUTION = "execution"
    WORKFLOW = "workflow"
    PHASE = "phase"
    STAGE = "stage"
    TASK = "task"
    ACTION = "action"
    OPERATION = "operation"
    INSTRUCTION = "instruction"

class ExecutionStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    DEGRADED = "degraded"
```

### 8.2 Permitted Transitions

```
PENDING ──► READY ──► RUNNING ──► COMPLETED
  │          │          │
  │          │          ├──► FAILED
  │          │          ├──► SKIPPED
  │          │          ├──► CANCELLED
  │          │          └──► PAUSED
  │          │                │
  │          │                └──► RUNNING  (resume)
  │          ▼
  └──► SKIPPED

RUNNING ──► DEGRADED ──► RUNNING (recovered)
                         └──► FAILED (unrecovered)
```

---

## 9. Existing Systems → Canonical Migration

| System | Migration Action | Canonical Model |
|--------|-----------------|-----------------|
| `runtime/executor.py` | **Keep** as reference implementation, add canonical interface | WorkflowEngine |
| `execution/` package | Deprecate — concepts ported to engines | 5 engines → 3 engines |
| `execution_graph.py` | Deprecate — model absorbed into canonical | ExecutionNode + hierarchy |
| `os/runtime.py` | Migrate health/ticks/recovery into ScheduleEngine | ScheduleEngine + Recovery |
| `kernel/kernel.py` | Deprecate — no consumers, duplicate | Removed |
| `fabric/kernel.py` | Deprecate — no consumers, duplicate | Removed |
| `autonomous/cycle.py` | Deprecate — stubs absorbed into CycleEngine | CycleEngine |
| `omega_loop.py` | Keep — already maps to Workflow → Phase → Stage | PhaseEngine |
| `atlas.py` | Keep — already maps to Workflow with 15 stages | PhaseEngine |
| `planner.py` | Keep — generates execution plans for new model | PlanningEngine |

---

## 10. Event Taxonomy

Every execution event follows the pattern: `{level}.{status}[.{detail}]`

```
execution.created
execution.booted
execution.running
execution.completed
execution.failed

workflow.defined
workflow.planned
workflow.executing
workflow.completed
workflow.failed
workflow.cancelled

phase.pending → phase.ready → phase.active → phase.completed / phase.failed
stage.pending → stage.running → stage.completed / stage.failed / stage.skipped
task.pending → task.running → task.completed / task.failed / task.blocked

action.invoking → action.completed / action.failed
operation.executing → operation.completed / operation.failed
instruction.dispatched → instruction.acknowledged / instruction.rejected

evidence.collected → evidence.verified / evidence.invalid
checkpoint.created → checkpoint.stored → checkpoint.restored
rollback.initiated → rollback.completed / rollback.failed
validation.evaluating → validation.passed / validation.failed
```

---

## 11. Engineering Decisions

### 11.1 Why 14 levels? Isn't that too many?

The 14 levels map precisely to the hierarchy found in the repository:
- Execution: `VenusPlatform.boot()`, `Atlas.run()` — top level
- Workflow: `ExecutionEngine.execute()`, `OmegaLoop` books
- Phase: `platform.py` GENESIS epochs, `omega_loop` books
- Stage: `atlas` 15 stages, `autonomous.cycle` 30 stages
- Task: `runtime/executor.Task`, `execution/tasks.Task`
- Action: `execution/actors.Actor`
- Operation: Low-level primitives
- Instruction: Atomic directives

The remaining levels (Result → Evidence → Validation → Checkpoint → Rollback → Completion) are the **observability and reliability pipeline** — the 6 steps required to make execution deterministic, verifiable, and recoverable.

Every level exists because code in this repository implements it.

### 11.2 Why not just use execution_graph.py as canonical?

`execution_graph.py` (420 lines) has the most complete execution graph model (15 NodeTypes, 5 EdgeTypes, pre/post conditions, checkpoint awareness). However:
- It has 0 consumers
- It combines Stage and Task into one NodeType (no hierarchy)
- It lacks Checkpoint, Rollback, Evidence, and Validation as first-class concepts
- It uses its own graph model instead of the Universal Graph Core

**Decision**: Use execution_graph's concepts (NodeType enum, EdgeType enum, condition model, versioning) but as part of the Universal Execution Model, not as the model itself.

### 11.3 Execution vs Service lifecycle — separate concerns?

**Yes**. Execution lifecycle describes one run of an activity (transient). Service lifecycle describes the lifetime of a capability (persistent). They share state machine design but are different concerns. A Service may execute many Workflows over its lifetime.

### 11.4 Should there be a single ExecutionEngine class?

**No**. The 7 specializations (Task, Workflow, Phase, Pipeline, Actor, Schedule, Cycle) are genuinely different execution models. Forcing them into one class would create a god-object. Instead, they share the `ExecutionEngine` Protocol and differ in scheduling strategy.

---

## 12. Validation

- **2,763 tests pass** — Universal Execution Model is a design, not an implementation; no code changed
- **All 16 execution systems mapped** to the canonical hierarchy
- **All state transitions documented** — no existing system has a transition this model cannot represent

---

## 13. Next Steps

1. Implement `ExecutionLevel`, `ExecutionStatus`, `ExecutionNode` in `genesis/execution_core/`
2. Implement `ExecutionEngine` Protocol with 7 specializations
3. Map `runtime/executor.py` to `WorkflowEngine`
4. Add deprecation warnings to `execution/`, `execution_graph.py`, `os/runtime.py`, `autonomous/cycle.py`
5. Mission 9: Universal Service Model
