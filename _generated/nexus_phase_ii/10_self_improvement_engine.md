# PROJECT NEXUS PHASE II — Mission 10: Self-Improvement Engine

**Date**: 2026-06-30

---

## 1. Vision

An autonomous pipeline that discovers problems, prioritizes them, simulates fixes, estimates risk, plans execution, verifies prerequisites, implements safe changes, runs validation, rolls back automatically, and records everything.

## 2. Current State

Manual steps currently performed by an engineer or AI:

```
Observe → Understand → Model → Design → Implement → Validate → Document
```

The goal is to automate this cycle:

```
Auto-observe → Auto-analyze → Auto-prioritize → Auto-simulate → 
Auto-implement (safe) → Auto-validate → Auto-rollback (if fail) → Auto-record
```

## 3. Architecture

### Pipeline Stages

```python
class ImprovementPipeline:
    """Autonomous self-improvement pipeline."""

    def __init__(self):
        self.discoverer = ProblemDiscoverer()
        self.prioritizer = ProblemPrioritizer()
        self.simulator = ImprovementSimulator()
        self.planner = ImprovementPlanner()
        self.verifier = PrerequisiteVerifier()
        self.executor = SafeExecutor()
        self.validator = ImprovementValidator()
        self.recorder = ImprovementRecorder()

    def run_cycle(self) -> ImprovementReport:
        # Stage 1: Discover problems
        problems = self.discoverer.discover()

        # Stage 2: Prioritize
        ranked = self.prioritizer.prioritize(problems)

        # Stage 3: Simulate (read-only)
        for problem in ranked[:3]:  # Top 3
            simulation = self.simulator.simulate(problem)

        # Stage 4: Plan (read-only)
        plan = self.planner.plan(ranked[0])

        # Stage 5: Verify prerequisites
        if not self.verifier.verify(plan):
            return ImprovementReport(status="BLOCKED", reason=verifier.obstacles)

        # Stage 6: Execute with safety checks
        result = self.executor.execute(plan)

        # Stage 7: Validate
        validation = self.validator.validate(result)

        # Stage 8: Rollback if needed
        if not validation.passed:
            self.executor.rollback(result)

        # Stage 9: Record
        report = self.recorder.record(problems, plan, result, validation)

        return report
```

### ProblemDiscoverer

```python
class ProblemDiscoverer:
    """Discovers improvement opportunities from multiple sources."""

    def discover(self) -> list[Problem]:
        problems = []

        # Source 1: Duplication analysis
        duplicates = self._find_duplicates()
        problems.extend(duplicates)

        # Source 2: Architecture analysis (Atlas integration)
        atlas_problems = self._load_atlas_findings()
        problems.extend(atlas_problems)

        # Source 3: Metric anomalies
        metric_issues = self._analyze_metrics()
        problems.extend(metric_issues)

        # Source 4: Deprecation tracking
        deprecation_issues = self._track_deprecations()
        problems.extend(deprecation_issues)

        # Source 5: Test health
        test_issues = self._analyze_test_health()
        problems.extend(test_issues)

        return problems

    def _find_duplicates(self) -> list[Problem]:
        """Check canonical registry for deprecated modules."""
        ...

    def _load_atlas_findings(self) -> list[Problem]:
        """Load Atlas Stage 6 problems."""
        ...

    def _analyze_metrics(self) -> list[Problem]:
        """Compare current metrics against targets."""
        ...
```

### ImprovementPlanner

```python
class ImprovementPlanner:
    """Plans the implementation steps for an improvement."""

    def plan(self, problem: Problem) -> ImprovementPlan:
        if problem.type == ProblemType.DUPLICATION:
            return self._plan_consolidation(problem)
        elif problem.type == ProblemType.ARCHITECTURE:
            return self._plan_architectural_fix(problem)
        elif problem.type == ProblemType.DEPENDENCY:
            return self._plan_dependency_fix(problem)
        # ...

    def _plan_consolidation(self, problem: Problem) -> ImprovementPlan:
        """Plan: mark deprecated, update consumers, remove."""
        return ImprovementPlan(
            steps=[
                PlanStep("add_deprecation_warning", files=[problem.source]),
                PlanStep("update_consumers", files=problem.consumers),
                PlanStep("update_canonical_registry"),
                PlanStep("run_tests"),
                PlanStep("remove_old_module"),  # Future cycle
            ],
            risk=self._estimate_risk(problem),
            estimated_effort=self._estimate_effort(problem),
        )
```

### SafeExecutor

```python
class SafeExecutor:
    """Executes improvements with automatic rollback capability."""

    def __init__(self):
        self._checkpoint = None

    def execute(self, plan: ImprovementPlan) -> ExecutionResult:
        # Create git checkpoint
        self._checkpoint = self._create_checkpoint()

        results = []
        for step in plan.steps:
            try:
                result = step.execute()
                results.append(result)
            except Exception as e:
                # Auto-rollback on any failure
                self.rollback(ExecutionResult(steps=results, error=str(e)))
                raise

        # Run validation suite
        if not self._run_validation():
            self.rollback(ExecutionResult(steps=results, error="Validation failed"))

        return ExecutionResult(steps=results, success=True)

    def rollback(self, result: ExecutionResult):
        """Restore checkpoint."""
        if self._checkpoint:
            self._restore_checkpoint(self._checkpoint)
        result.rolled_back = True

    def _create_checkpoint(self) -> str:
        """Create git commit or stash for rollback."""
        ...

    def _run_validation(self) -> bool:
        """Run test suite, check metrics."""
        ...
```

## 4. Integration with Existing Systems

### Atlas Integration
- Atlas Stage 6 (Problems) feeds ProblemDiscoverer
- Atlas Stage 12 (Roadmap) feeds prioritizer

### OmegaLoop Integration
- Book XII (Self Evolution) triggers ImprovementPipeline.run_cycle()
- Book XIV (Continuous Convergence) tracks improvement progress

### EngineeringKnowledgeStore Integration
- Every improvement cycle is recorded as KnowledgeArtifact
- Past cycles are queried to avoid repeated mistakes

## 5. Risk Analysis

| Risk | Severity | Mitigation |
|------|----------|------------|
| Auto-implementation breaks code | HIGH | Git checkpoint + auto-rollback |
| Wrong priority selection | MEDIUM | Human-in-the-loop for P0 changes |
| Incomplete rollback | MEDIUM | Full git restore, not partial |
| Test suite false positives | LOW | Manual verification step configurable |
| Circular improvement loops | MEDIUM | Rate limiting, diversity checks |

## 6. Effort

| Component | Effort | Risk |
|-----------|--------|------|
| ProblemDiscoverer | 1d | None (read-only) |
| ImprovementPlanner | 2d | Low (read-only) |
| SafeExecutor | 3d | HIGH (writes code) |
| ImprovementValidator | 1d | Low |
| ImprovementRecorder | 0.5d | None |
| Pipeline orchestration | 1d | Low |
| **Total** | **8.5d** | |
