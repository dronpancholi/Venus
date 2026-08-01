# PROJECT NEXUS PHASE II — Mission 5: Universal Execution Model

**Date**: 2026-06-30

---

## 1. Current Fragmentation

Genesis has at least 7 distinct execution models with incompatible APIs:

| System | Lines | Execution Model | State | Lifecycle |
|--------|-------|----------------|-------|-----------|
| OmegaLoop | 6,575 | Sequential 18-Phase | Implicit (self.*) | run() |
| Atlas | 1,297 | Sequential 15-Stage | Implicit (self.*) | run() |
| Platform | 747 | Service lifecycle | Explicit attributes | boot() -> run() -> shutdown() |
| OS Runtime | 499 | Tick-based loop | ComponentStatus | start() -> tick() -> stop() |
| ExecutionEngine | 105 | Workflow/Task | TaskStatus | execute(workflow) |
| Planner | 315 | Plan tree | PlanNode | create() -> execute() |
| Autonomous Cycle | 133 | Observe-Plan-Act | Cycle state | run_cycle() |

Each has its own: phase/task/step model, status enum, error handling, reporting, persistence.

## 2. Unified Model

### Core Abstractions

```python
@dataclass
class ExecutionContext:
    """Shared context for a complete execution run."""
    run_id: str
    started_at: datetime
    config: dict[str, Any]
    artifacts: dict[str, Any]  # shared state between phases

class ExecutionPhase(ABC):
    """Single atomic unit of executable work."""
    name: str
    phase_number: int

    @abstractmethod
    def execute(self, ctx: ExecutionContext) -> PhaseResult: ...

@dataclass
class PhaseResult:
    phase: str
    status: PhaseStatus
    data: dict[str, Any]
    metrics: dict[str, float]
    errors: list[str]
    duration_ms: float
    artifacts_created: list[str]

class PhaseStatus(Enum):
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3
    SKIPPED = 4
    ROLLED_BACK = 5
```

### Pipeline (Sequential)

```python
class ExecutionPipeline:
    """Ordered sequence of phases. Stops on first failure."""

    def __init__(self, phases: list[ExecutionPhase]):
        self.phases = phases

    def run(self, ctx: ExecutionContext) -> list[PhaseResult]:
        results = []
        for phase in self.phases:
            start = time.time()
            result = phase.execute(ctx)
            result.duration_ms = (time.time() - start) * 1000
            results.append(result)
            if result.status == PhaseStatus.FAILED:
                break
        return results
```

### Execution Graph (DAG)

```python
class ExecutionGraph:
    """DAG of phases with dependency resolution."""

    def __init__(self):
        self._phases: dict[str, ExecutionPhase] = {}
        self._deps: dict[str, list[str]] = {}

    def add_phase(self, phase: ExecutionPhase, depends_on: list[str] | None = None):
        self._phases[phase.name] = phase
        self._deps[phase.name] = depends_on or []

    def run(self, ctx: ExecutionContext) -> list[PhaseResult]:
        order = topological_sort(self._deps)
        results = []
        for name in order:
            phase = self._phases[name]
            result = phase.execute(ctx)
            results.append(result)
        return results
```

## 3. Adapter Pattern

Each existing execution system gets an adapter implementing ExecutionPhase.

### OmegaLoop Adapter
```python
class OmegaLoopPhase(ExecutionPhase):
    """Wraps OmegaLoop as an ExecutionPhase."""

    def __init__(self, omega_loop: OmegaLoop):
        super().__init__(name="omegaloop", phase_number=10)
        self._omega = omega_loop

    def execute(self, ctx: ExecutionContext) -> PhaseResult:
        try:
            self._omega.run()
            return PhaseResult(
                phase=self.name, status=PhaseStatus.COMPLETED,
                data={"books_completed": 18}, metrics={}, errors=[],
                duration_ms=0, artifacts_created=[],
            )
        except Exception as e:
            return PhaseResult(
                phase=self.name, status=PhaseStatus.FAILED,
                data={}, metrics={}, errors=[str(e)],
                duration_ms=0, artifacts_created=[],
            )
```

### Atlas Adapter
```python
class AtlasPhase(ExecutionPhase):
    """Wraps Atlas as an ExecutionPhase."""

    def __init__(self, atlas: AtlasEngine):
        super().__init__(name="atlas", phase_number=5)
        self._atlas = atlas

    def execute(self, ctx: ExecutionContext) -> PhaseResult:
        try:
            self._atlas.run()
            return PhaseResult(phase=self.name, status=PhaseStatus.COMPLETED, ...)
        except Exception as e:
            return PhaseResult(phase=self.name, status=PhaseStatus.FAILED, errors=[str(e)], ...)
```

### Platform Boot Adapter
```python
class PlatformBootPhase(ExecutionPhase):
    """Platform bootstrap + boot as phases."""

    def __init__(self, platform: VenusPlatform):
        super().__init__(name="platform_boot", phase_number=1)
        self._platform = platform

    def execute(self, ctx: ExecutionContext) -> PhaseResult:
        try:
            self._platform.bootstrap().boot()
            return PhaseResult(phase=self.name, status=PhaseStatus.COMPLETED, ...)
        except Exception as e:
            return PhaseResult(phase=self.name, status=PhaseStatus.FAILED, ...)
```

## 4. Composed Pipeline

```python
# Full execution as a unified pipeline
pipeline = ExecutionPipeline([
    PlatformBootPhase(platform),           # 1. Boot infrastructure
    CanonicalInitPhase(),                   # 2. Initialize canonical registry
    MetaModelPhase(meta_model),             # 3. Build meta model
    AtlasPhase(atlas),                      # 4. Run Atlas analysis
    OmegaLoopPhase(omega_loop),            # 5. Run OmegaLoop constitution
    ReportGenerationPhase(),                # 6. Generate all reports
    PlatformShutdownPhase(platform),        # 7. Graceful shutdown
])

ctx = ExecutionContext(
    run_id=generate_id("run"),
    started_at=datetime.now(timezone.utc),
    config={"workspace": "/path/to/repo"},
    artifacts={},
)

results = pipeline.run(ctx)
for r in results:
    print(f"[{r.status.name}] {r.phase}: {r.duration_ms:.0f}ms")
```

## 5. Migration Cost & Value

| Step | Effort | Impact |
|------|--------|--------|
| Core model (Phase, Result, Pipeline, Graph) | 0.5d | Foundation |
| PhaseStatus enum | 0.1d | Shared across all |
| OmegaLoop adapter | 0.5d | Wraps 6,575 lines |
| Atlas adapter | 0.5d | Wraps 1,297 lines |
| Platform adapters (bootstrap/boot/shutdown) | 0.5d | Decomposes 747 lines |
| OS Runtime adapter | 0.5d | Wraps 499 lines |
| ExecutionEngine adapter | 0.3d | Wraps 105 lines |
| Planner adapter | 0.3d | Wraps 315 lines |
| Phase registry + CLI | 0.5d | Usability |
| **Total** | **3.7d** | |

## 6. Benefits

1. **Unified observability**: All executions produce PhaseResult — single pipeline for metrics, reporting, alerting
2. **Composability**: Mix Atlas/OmegaLoop/Platform phases in any order
3. **Pluggability**: New system implements 1 method -> automatically part of pipeline
4. **Rollback**: Failed phases trigger compensating rollback phases
5. **Parallelism**: ExecutionGraph runs independent phases concurrently
6. **Testing**: Each phase testable in isolation with mock execution context

## 7. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Adapters hide system-specific errors | Low | PhaseResult.errors captures full traceback |
| Shared mutable state via ExecutionContext | Medium | Clear read/write conventions, immutability by default |
| Performance overhead | Low | Single dict per phase result |
| Each adapter must handle partial execution | Medium | Adapters check PhaseStatus before executing |
