from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any, Callable

from genesis.utils.identity import generate_id


class CycleStage(Enum):
    # Canonical Ω stages
    OBSERVE = "observe"
    ACQUIRE = "acquire"
    UNDERSTAND = "understand"
    REPRESENT = "represent"
    REASON = "reason"
    PREDICT = "predict"
    PLAN = "plan"
    RESEARCH = "research"
    EXPERIMENT = "experiment"
    SIMULATE = "simulate"
    VALIDATE = "validate"
    IMPLEMENT = "implement"
    COMPILE = "compile"
    TEST = "test"
    BENCHMARK = "benchmark"
    SECURE = "secure"
    DEPLOY = "deploy"
    MONITOR = "monitor"
    REFLECT = "reflect"
    LEARN = "learn"
    REMEMBER = "remember"
    IMPROVE = "improve"
    REPEAT = "repeat"
    # Genesis internal stages (mapped into the canonical flow)
    BUILD_IR = "build_ir"
    BUILD_TWIN = "build_twin"
    UPDATE_GRAPH = "update_graph"
    UPDATE_BRAIN = "update_brain"
    HYPOTHESIS = "hypothesis"
    GENERATE_PATCH = "generate_patch"
    RUN_TESTS = "run_tests"
    PUBLISH = "publish"


CYCLE_ORDER = [
    CycleStage.OBSERVE, CycleStage.ACQUIRE, CycleStage.UNDERSTAND,
    CycleStage.REPRESENT, CycleStage.REASON, CycleStage.PREDICT,
    CycleStage.PLAN, CycleStage.RESEARCH, CycleStage.EXPERIMENT,
    CycleStage.SIMULATE, CycleStage.VALIDATE, CycleStage.IMPLEMENT,
    CycleStage.COMPILE, CycleStage.TEST, CycleStage.BENCHMARK,
    CycleStage.SECURE, CycleStage.DEPLOY, CycleStage.MONITOR,
    CycleStage.REFLECT, CycleStage.LEARN, CycleStage.REMEMBER,
    CycleStage.IMPROVE, CycleStage.REPEAT,
    # Genesis internal stages (injected into the canonical flow)
    CycleStage.BUILD_IR, CycleStage.BUILD_TWIN, CycleStage.UPDATE_GRAPH,
    CycleStage.UPDATE_BRAIN, CycleStage.HYPOTHESIS,
    CycleStage.GENERATE_PATCH, CycleStage.RUN_TESTS, CycleStage.PUBLISH,
]


@dataclass
class CycleResult:
    stage: CycleStage = CycleStage.OBSERVE
    status: str = "pending"
    started_at: float = 0.0
    completed_at: float = 0.0
    output: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        end = self.completed_at or time.time()
        return (end - self.started_at) * 1000

    @property
    def success(self) -> bool:
        return self.status == "completed" and not self.errors


@dataclass
class CycleRun:
    id: str = ""
    started_at: float = 0.0
    completed_at: float = 0.0
    status: str = "running"
    results: dict[str, CycleResult] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    error: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("cycle", 14)
        if not self.started_at:
            self.started_at = time.time()

    @property
    def duration_ms(self) -> float:
        end = self.completed_at or time.time()
        return (end - self.started_at) * 1000

    @property
    def all_success(self) -> bool:
        return all(r.success for r in self.results.values())


class AutonomousEngine:
    """The complete autonomous engineering cycle — Observe → ... → Learn → Repeat."""

    def __init__(self):
        self._handlers: dict[CycleStage, Callable] = {}
        self._history: list[CycleRun] = []
        self._lock = RLock()
        self._running = False

    def register(self, stage: CycleStage, handler: Callable):
        self._handlers[stage] = handler

    def run(self, initial_context: dict[str, Any] | None = None) -> CycleRun:
        run = CycleRun(context=dict(initial_context or {}))
        with self._lock:
            self._history.append(run)
        for stage in CYCLE_ORDER:
            handler = self._handlers.get(stage)
            result = CycleResult(stage=stage, started_at=time.time())
            if handler:
                try:
                    output = handler(run.context)
                    result.output = output if isinstance(output, dict) else {"result": output}
                    result.status = "completed"
                except Exception as e:
                    result.status = "failed"
                    result.errors = [str(e)]
                    run.status = "failed"
                    run.error = str(e)
            else:
                result.status = "skipped"
            result.completed_at = time.time()
            run.results[stage.value] = result
            if result.status == "failed":
                break
        run.status = "completed" if run.status != "failed" else "failed"
        run.completed_at = time.time()
        run.metrics = self._compute_metrics(run)
        return run

    def run_continuous(self, interval_secs: float = 300.0):
        self._running = True
        while self._running:
            self.run()
            time.sleep(interval_secs)

    def stop(self):
        self._running = False

    def _compute_metrics(self, run: CycleRun) -> dict[str, float]:
        metrics: dict[str, float] = {}
        completed = [r for r in run.results.values() if r.status == "completed"]
        failed = [r for r in run.results.values() if r.status == "failed"]
        metrics["total_stages"] = float(len(run.results))
        metrics["completed_stages"] = float(len(completed))
        metrics["failed_stages"] = float(len(failed))
        metrics["total_duration_ms"] = run.duration_ms
        if completed:
            metrics["avg_stage_ms"] = sum(r.duration_ms for r in completed) / len(completed)
        return metrics

    def history(self, limit: int = 10) -> list[CycleRun]:
        return list(self._history[-limit:])

    def last_run(self) -> CycleRun | None:
        return self._history[-1] if self._history else None

    def summary(self) -> dict[str, Any]:
        total = len(self._history)
        succeeded = sum(1 for r in self._history if r.status == "completed")
        return {
            "total_cycles": total,
            "succeeded": succeeded,
            "failed": total - succeeded,
            "last_duration_ms": self._history[-1].duration_ms if self._history else 0.0,
            "running": self._running,
        }
